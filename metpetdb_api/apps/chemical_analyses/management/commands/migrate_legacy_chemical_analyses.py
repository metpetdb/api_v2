from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management import BaseCommand

from apps.chemical_analyses.models import (
    ChemicalAnalysis,
    ChemicalAnalysisElement,
    ChemicalAnalysisOxide,
)
from apps.chemical_analyses.shared_models import Element, Oxide
from apps.common.utils import queryset_iterator
from apps.samples.models import (
    Mineral,
    MineralType,
    Sample,
    SampleMapping,
    Subsample,
    Reference,
)

from apps.images.models import Image, ImageMapping

from legacy.models import (
    ChemicalAnalyses as LegacyChemicalAnalyses,
    ChemicalAnalysisElements as LegacyChemicalAnalysisElements,
    ChemicalAnalysisOxides as LegacyChemicalAnalysisOxides,
    Elements as LegacyElement,
    MineralTypes as LegacyMineralType,
    Oxides as LegacyOxide,
    ElementMineralTypes as LegacyElementMineralType,
    OxideMineralTypes as LegacyOxideMineralType,
)


class Command(BaseCommand):
    help = 'Migrates legacy chemical analyses to the new data model'

    def handle(self, *args, **options):
        self._migrate_elements()
        self._migrate_oxides()
        self._migrate_mineral_types()
        self._migrate_chemical_analyses()


    @transaction.atomic
    def _migrate_chemical_analyses(self):
        print("Migrating chemical analyses...")
        User = get_user_model()
        all_references = []

        old_chemical_analyses = queryset_iterator(
            LegacyChemicalAnalyses
            .objects
            .all()
            .select_related('subsample', 'reference', 'user')
        )

        ChemicalAnalysis.objects.all().delete()
        for record in old_chemical_analyses:
            print("Migrating chemical analyses: #{}".format(record.pk))
            if record.large_rock == 'Y':
                mineral = Mineral.objects.get(name='Bulk Rock')
            else:
                try:
                    mineral = Mineral.objects.get(name=record.mineral.name)
                except AttributeError:
                    mineral = None

            if record.reference:
                all_references.append(record.reference.name)

            subsample = Subsample.objects.get(
                name=record.subsample.name,
                sample=Sample.objects.get(
                    pk=SampleMapping.objects.get(
                        old_sample_id=record.subsample.sample.pk
                    ).new_sample_id)
            )

            try:
                reference=record.reference.name
            except AttributeError:
                reference = None

            try:
                reference_image = Image.objects.get(
                    subsample=subsample,
                    pk=ImageMapping.objects.get(
                        old_image_id=record.image.pk).new_image_id)
            except Image.DoesNotExist:
                reference_image = None
            except AttributeError:
                reference_image = None

            chem_analysis = ChemicalAnalysis.objects.create(
                subsample=subsample,
                public_data=True if record.public_data == 'Y' else False,
                reference_x=record.reference_x,
                reference_y=record.reference_y,
                stage_x = record.stage_x,
                stage_y = record.stage_y,
                analysis_method = record.analysis_method,
                where_done = record.where_done,
                analyst = record.analyst,
                analysis_date = record.analysis_date,
                date_precision = record.date_precision,
                description = record.description,
                total = record.total,
                spot_id = record.spot_id,
                mineral=mineral,
                owner=User.objects.get(email=record.user.email),
                reference=reference,
                reference_image=reference_image
            )

            legacy_cae = LegacyChemicalAnalysisElements.objects.filter(
                chemical_analysis=record
            ).select_related('element')

            for cae in legacy_cae:
                ChemicalAnalysisElement.objects.create(
                    chemical_analysis=chem_analysis,
                    element=Element.objects.get(name=cae.element.name),
                    amount=cae.amount,
                    precision = cae.precision,
                    precision_type = cae.precision_type,
                    measurement_unit = cae.measurement_unit,
                    min_amount = cae.min_amount,
                    max_amount = cae.max_amount,
                )

            legacy_cao = LegacyChemicalAnalysisOxides.objects.filter(
                chemical_analysis=record
            ).select_related('oxide')

            for cao in legacy_cao:
                ChemicalAnalysisOxide.objects.create(
                    chemical_analysis=chem_analysis,
                    oxide=Oxide.objects.get(species=cao.oxide.species),
                    amount=cao.amount,
                    precision = cao.precision,
                    precision_type = cao.precision_type,
                    measurement_unit = cao.measurement_unit,
                    min_amount = cao.min_amount,
                    max_amount = cao.max_amount,
                )

        if all_references:
            for ref in all_references:
                Reference.objects.get_or_create(name=ref)


    @transaction.atomic
    def _migrate_elements(self):
        print("Migrating elements...")
        old_elements = LegacyElement.objects.all()

        Element.objects.all().delete()
        for record in old_elements:
            Element.objects.create(
                name=record.name,
                alternate_name=record.alternate_name,
                symbol=record.symbol,
                atomic_number=record.atomic_number,
                weight=record.weight,
                order_id=record.order_id,
            )


    @transaction.atomic
    def _migrate_oxides(self):
        print("Migrating oxides...")
        old_oxides = LegacyOxide.objects.all()

        Oxide.objects.all().delete()
        for record in old_oxides:
            Oxide.objects.create(
                element=Element.objects.get(name=record.element.name),
                oxidation_state=record.oxidation_state,
                species=record.species,
                weight=record.weight,
                cations_per_oxide=record.cations_per_oxide,
                conversion_factor=record.conversion_factor,
                order_id=record.order_id,
            )


    @transaction.atomic
    def _migrate_mineral_types(self):
        print("Migrating mineral types...")
        old_mineral_types = LegacyMineralType.objects.all()

        MineralType.objects.all().delete()
        for record in old_mineral_types:
            old_emts = LegacyElementMineralType.objects.filter(
                mineral_type=record)
            element_names = (emt.element.name for emt in old_emts)
            elements = Element.objects.filter(name__in=element_names)

            old_oxmts = LegacyOxideMineralType.objects.filter(
                mineral_type=record)
            oxide_species = (oxmt.oxide.species for oxmt in old_oxmts)
            oxides = Oxide.objects.filter(species__in=oxide_species)

            min_type = MineralType.objects.create(name=record.name)
            min_type.elements.add(*elements)
            min_type.oxides.add(*oxides)
