from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction

from apps.samples.models import (
    MetamorphicGrade,
    MetamorphicRegion,
    RockType,
    Sample,
    Region, Reference, Collector, Mineral, SampleMineral, Subsample,
    SubsampleType, Grid)

from legacy.models import (
    Grids as LegacyGrid,
    MetamorphicGrades as LegacyMetamorphicGrade,
    MetamorphicRegions as LegacyMetamorphicRegion,
    Minerals as LegacyMineral,
    RockType as LegacyRockType,
    SampleMetamorphicRegions as LegacySampleMetamorphicRegion,
    SampleMetamorphicGrades as LegacySampleMetamorphicGrades,
    SampleMinerals as LegacySampleMineral,
    Samples as LegacySample,
    Subsamples as LegacySubsample,
    SubsampleType as LegacySubsampleType,
    SampleAliases as LegacySampleAlias,
    SampleRegions as LegacySampleRegion,
    SampleReference as LegacySampleReference,
    Users as LegacyUser,
)

class Command(BaseCommand):
    help = 'Migrates legacy samples to the new data model'

    @transaction.atomic
    def handle(self, *args, **options):
        self._migrate_rock_types()
        self._migrate_metamorphic_grades()
        self._migrate_metamorphic_regions()
        self._migrate_minerals()
        self._migrate_subsample_types()
        self._migrate_samples()


    def _migrate_samples(self):
        print("Migrating samples...")
        User = get_user_model()

        all_collectors = []
        all_regions = []
        all_references = []

        old_samples = LegacySample.objects.all()
        Sample.objects.all().delete()

        for old_sample in old_samples:
            print("Migrating old sample #{0}: {1}"
                  .format(old_sample.pk, old_sample.number))
            rock_type = (RockType
                         .objects
                         .filter(name=old_sample.rock_type.rock_type)[0])

            old_user = LegacyUser.objects.get(pk=old_sample.user_id)
            new_user = User.objects.get(email=old_user.email)

            if old_sample.collector:
                all_collectors.extend([old_sample.collector])

            regions = [lsr.region.name
                       for lsr in LegacySampleRegion
                           .objects
                           .filter(sample=old_sample)]
            if regions:
                all_regions.extend(regions)

            references = [lsr.reference.name
                          for lsr in LegacySampleReference
                                     .objects
                                     .filter(sample=old_sample)]
            if references:
                all_references.extend(references)

            old_metamorphic_regions = (lsa.metamorphic_region.name
                                       for lsa in
                                       LegacySampleMetamorphicRegion
                                       .objects
                                       .filter(sample=old_sample))
            new_metamorphic_regions = (
                MetamorphicRegion
                .objects
                .filter(name__in=old_metamorphic_regions)
            )

            old_metamorphic_grades = (lsa.metamorphic_grade.name
                                      for lsa in
                                      LegacySampleMetamorphicGrades
                                      .objects
                                      .filter(sample=old_sample))
            new_metamorphic_grades = (MetamorphicGrade
                                      .objects
                                      .filter(name__in=old_metamorphic_grades))

            aliases = [lsa.alias
                       for lsa in LegacySampleAlias
                           .objects
                           .filter(sample=old_sample)]

            new_sample = Sample.objects.create(
                public_data=True if old_sample.public_data == 'Y' else False,
                number=old_sample.number,
                user=new_user,
                aliases=aliases,
                collection_date=old_sample.collection_date,
                date_precision=old_sample.date_precision,
                country=old_sample.country,
                description=old_sample.description,
                location_name=old_sample.location_text,
                location_coords=old_sample.location,
                location_error=old_sample.location_error,
                rock_type=rock_type,
                regions=regions,
                references=references,
                collector_name=old_sample.collector
            )

            self._migrate_subsamples(old_sample, new_sample)

            new_sample.metamorphic_regions.add(*new_metamorphic_regions)
            new_sample.metamorphic_grades.add(*new_metamorphic_grades)

            old_minerals = (LegacySampleMineral
                            .objects
                            .filter(sample=old_sample))
            old_mineral_names = [om.mineral.name for om in old_minerals]
            new_minerals = Mineral.objects.filter(name__in=old_mineral_names)

            for mineral in new_minerals:
                old_sample_mineral = (LegacySampleMineral
                                      .objects
                                      .get(mineral__name=mineral.name,
                                           sample=old_sample))
                SampleMineral.objects.create(sample=new_sample,
                                             mineral=mineral,
                                             amount=old_sample_mineral.amount)


        Region.objects.all().delete()
        Region.objects.bulk_create([Region(name=region)
                                    for region in set(all_regions)])

        Reference.objects.all().delete()
        Reference.objects.bulk_create([Reference(name=reference)
                                       for reference in set(all_references)])

        Collector.objects.all().delete()
        Collector.objects.bulk_create([Collector(name=collector)
                                       for collector in set(all_collectors)])


    def _migrate_subsamples(self, old_sample, new_sample):
        print("Migrating subsamples...")
        old_records = LegacySubsample.objects.filter(sample=old_sample)

        for record in old_records:
            new_user = get_user_model().objects.get(email=record.user.email)
            subsample_type = SubsampleType.objects.get(
                name=record.subsample_type.subsample_type
            )
            subsample = Subsample.objects.create(
                name=record.name,
                sample=new_sample,
                public_data=record.public_data,
                user=new_user,
                subsample_type=subsample_type
            )

            old_grids = LegacyGrid.objects.filter(subsample=record)
            if old_grids:
                for grid in old_grids:
                    Grid.objects.create(subsample=subsample,
                                        width=grid.width,
                                        height=grid.height,
                                        public_data=grid.public_data)


    def _migrate_subsample_types(self):
        print("Migrating legacy subsample types...")
        old_records = LegacySubsampleType.objects.all()

        for record in old_records:
            SubsampleType.objects.create(name=record.subsample_type)


    def _migrate_rock_types(self):
        print("Migrating rock types...")
        old_records = LegacyRockType.objects.all()
        RockType.objects.all().delete()

        for record in old_records:
            RockType.objects.create(name=record.rock_type)


    def _migrate_metamorphic_grades(self):
        print("Migrating metamorphic grades...")
        old_records = LegacyMetamorphicGrade.objects.all()
        MetamorphicGrade.objects.all().delete()

        for record in old_records:
            MetamorphicGrade.objects.create(name=record.name)


    def _migrate_metamorphic_regions(self):
        print("Migrating metamorphic regions...")
        old_records = LegacyMetamorphicRegion.objects.all()
        MetamorphicRegion.objects.all().delete()

        for record in old_records:
            MetamorphicRegion.objects.create(
                name=record.name,
                shape=record.shape,
                description=record.description,
                label_location=record.label_location
            )


    def _migrate_minerals(self):
        print("Migrating minerals...")
        old_records = LegacyMineral.objects.all()
        Mineral.objects.all().delete()

        for record in old_records:
            Mineral.objects.create(name=record.name)

        for record in old_records:
            mineral = Mineral.objects.get(name=record.name)
            mineral.real_mineral = (Mineral
                                    .objects
                                    .get(name=record.real_mineral.name))
            mineral.save()
