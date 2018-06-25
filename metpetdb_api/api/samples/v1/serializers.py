from rest_framework import serializers

from api.lib.serializers import DynamicFieldsModelSerializer
from api.users.v1.serializers import UserSerializer

from apps.chemical_analyses.models import ChemicalAnalysis
from apps.samples.models import (
    MetamorphicGrade,
    GeoReference,
    MetamorphicRegion,
    RockType,
    Sample,
    Mineral,
    SampleMineral,
    Region,
    Reference,
    Collector,
    Subsample,
    SubsampleType,
)
from apps.users.models import User

SAMPLE_FIELDS = ('number', 'aliases', 'collection_date', 'description',
                 'location_name', 'location_coords', 'location_error',
                 'date_precision', 'country', 'regions', 'collector_name',
                 'collector_id', 'sesar_number',)

SUBSAMPLE_FIELDS = ('name')

class RockTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RockType


class MineralSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Mineral


class SampleMineralSerializer(DynamicFieldsModelSerializer):
    id = serializers.ReadOnlyField(source='mineral.id')
    name = serializers.ReadOnlyField(source='mineral.name')
    real_mineral_id = serializers.ReadOnlyField(
                          source='mineral.real_mineral_id'
                      )
    class Meta:
        model = SampleMineral
        fields = ('id', 'name', 'amount', 'real_mineral_id',)


class SampleSerializer(DynamicFieldsModelSerializer):
    minerals = SampleMineralSerializer(source='samplemineral_set',
                                       many=True)
    # owner = UserSerializer(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    rock_type = serializers.SerializerMethodField(read_only=True)
    metamorphic_grades = serializers.SerializerMethodField(read_only=True)
    metamorphic_regions = serializers.SerializerMethodField(read_only=True)
    minerals = serializers.SerializerMethodField(read_only=True)
    references = serializers.SerializerMethodField(read_only=True)
    latitude = serializers.SerializerMethodField(read_only=True)
    longitude = serializers.SerializerMethodField(read_only=True)

    # TODO: figure out if there is a better, more efficient way to do this
    subsample_ids = serializers.SerializerMethodField()
    chemical_analyses_ids = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        depth = 1
        fields = (
            'number',
            'owner',
            'regions',
            'country',
            'rock_type',
            'metamorphic_grades',
            'metamorphic_regions',
            'minerals',
            'references',
            'longitude',
            'latitude',
            # 'igsn',
            'collector_name',
            'collection_date',
            'location_name',
            'description',
            'subsample_ids',
            'chemical_analyses_ids',
            )

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if self.initial_data.get('owner'):
            self._validated_data.update(
                {'owner': User.objects.get(pk=self.initial_data['owner'])})

        if self.initial_data.get('rock_type_id'):
            self._validated_data.update(
                {'rock_type': (RockType
                               .objects
                               .get(pk=self.initial_data['rock_type_id']))
                 }
            )

        return not bool(self._errors)

    def create(self, validated_data):
        if validated_data.get('samplemineral_set'):
            del validated_data['samplemineral_set']

        instance = super().create(validated_data)
        return instance


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in SAMPLE_FIELDS:
                setattr(instance, attr, value)
        instance.save()

        return instance

    def get_owner(self,obj):
        return obj.owner.name

    def get_rock_type(self,obj):
        return obj.rock_type.name

    def get_metamorphic_grades(self,obj):
        grades = []
        for g in obj.metamorphic_grades.all():
            grades.append(g.name)
        return grades

    def get_metamorphic_regions(self,obj):
        regions = []
        for r in obj.metamorphic_regions.all():
            regions.append(r.name)
        return regions

    def get_minerals(self,obj):
        minerals = []
        for m in obj.samplemineral_set.all():
            minerals.append(m.mineral.name)
        return minerals

    def get_references(self,obj):
        references = []
        for r in obj.references.all():
            references.append(r.name)
        return references

    def get_longitude(self,obj):
        return round(obj.location_coords[0],5)

    def get_latitude(self,obj):
        return round(obj.location_coords[1],5)

    def get_subsample_ids(self, obj):
        return Subsample.objects.filter(sample_id=obj.pk).values_list('id', flat=True)

    def get_chemical_analyses_ids(self, obj):
        subsample_ids = obj.subsamples.values_list('id', flat=True)
        return ChemicalAnalysis.objects.filter(
            subsample_id__in=subsample_ids).values_list('id', flat=True)


class SubsampleSerializer(DynamicFieldsModelSerializer):
    sample = SampleSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Subsample
        depth = 1

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if self.initial_data.get('owner'):
            self._validated_data.update(
                {'owner': User.objects.get(pk=self.initial_data['owner'])})
        
        if self.initial_data.get('sample'):
            self._validated_data.update(
                {'sample': (Sample
                               .objects
                               .get(pk=self.initial_data['sample']))
                 }
            )
        
        if self.initial_data.get('subsample_type'):
            self._validated_data.update(
                {'subsample_type': (SubsampleType
                               .objects
                               .get(pk=self.initial_data['subsample_type']))
                 }
            )
        
        return not bool(self._errors)

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in SUBSAMPLE_FIELDS:
                setattr(instance, attr, value)
        instance.save()

        return instance    


class SubsampleTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = SubsampleType
        depth = 1


class MetamorphicGradeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicGrade


class MetamorphicRegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicRegion


class GeoReferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = GeoReference

class RegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Region


class ReferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Reference


class CollectorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Collector

class SampleSearchSerializer(SampleSerializer):
    Sample = serializers.SerializerMethodField(read_only=True)
    Rock_Type = serializers.SerializerMethodField(read_only=True)
    Comment = serializers.SerializerMethodField(read_only=True)
    Latitude = serializers.SerializerMethodField(read_only=True)
    Longitude = serializers.SerializerMethodField(read_only=True)
    Location_Error = serializers.SerializerMethodField(read_only=True)
    Region = serializers.SerializerMethodField(read_only=True)
    Country = serializers.SerializerMethodField(read_only=True)
    Collector = serializers.SerializerMethodField(read_only=True)
    Date_of_Collection = serializers.SerializerMethodField(read_only=True)
    Present_Sample_Location = serializers.SerializerMethodField(read_only=True)
    Reference = serializers.SerializerMethodField(read_only=True)
    Metamorphic_Grade = serializers.SerializerMethodField(read_only=True)
    Minerals = serializers.SerializerMethodField(read_only=True)
    Subsamples = serializers.SerializerMethodField(read_only=True)
    Chemical_Analyses = serializers.SerializerMethodField(read_only=True)


    def get_Sample(self,obj):
        return obj.number

    def get_Rock_Type(self,obj):
        return obj.rock_type.name

    def get_Comment(self,obj):
        return obj.description

    def get_Latitude(self,obj):
        return round(obj.location_coords[1],5)

    def get_Longitude(self,obj):
        return round(obj.location_coords[0],5)

    def get_Location_Error(self,obj):
        return obj.location_error

    def get_Region(self,obj):
        regions = []
        for r in obj.regions:
            regions.append(r)
        return regions

    def get_Country(self,obj):
        return obj.country

    def get_Collector(self,obj):
        return obj.collector_name

    def get_Date_of_Collection(self,obj):
        return str(obj.collection_date).split(' ')[0]

    def get_Present_Sample_Location(self,obj):
        return obj.location_name

    def get_Reference(self,obj):
        return obj.references.name

    def get_Metamorphic_Grade(self,obj):
        return obj.metamorphic_grades.name

    def get_Minerals(self,obj):
        minerals = []
        for m in obj.samplemineral_set.all():
            minerals.append(m.mineral.name)
        return minerals

    def get_Subsamples(self,obj):
        return len(Subsample.objects.filter(sample_id=obj.pk).values_list('id',flat=True))

    def get_Chemical_Analyses(self,obj):
        subsample_ids = obj.subsamples.values_list('id', flat=True)
        return len(ChemicalAnalysis.objects.filter(
            subsample_id__in=subsample_ids).values_list('id', flat=True))

    class Meta:
        model = Sample
        fields = (
            'Sample',
            'Rock_Type',
            'Comment',
            'Latitude',
            'Longitude',
            'Location_Error',
            'Region',
            'Country',
            'Collector',
            'Date_of_Collection',
            'Present_Sample_Location',
            'Reference',
            'Metamorphic_Grade',
            'Minerals',
            'Subsamples',
            'Chemical_Analyses',
            )