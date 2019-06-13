from rest_framework import serializers

from api.lib.serializers import DynamicFieldsModelSerializer
from api.users.v1.serializers import UserSerializer
from api.images.v1.serializers import ImageSerializer

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

SAMPLE_FIELDS = ('id', #
                 'number', 
                 # 'aliases', 
                 'owner', #
                 'regions', 
                 'country',
                 'rock_type', #
                 'metamorphic_grades', #
                 'metamorphic_regions', #
                 'minerals', #
                 'references', #
                 'longitude',
                 'latitude',
                 #'location_coords', 
                 'location_error',
                 'sesar_number', 
                 'collector_name',
                 # 'collector_id', 
                 'collection_date', 
                 # 'date_precision', 
                 'location_name', 
                 'description',
                 # 'image', 
                 'images',
                 'subsample_ids', #
                 'chemical_analyses_ids', #
                 'public_data',)

SUBSAMPLE_FIELDS = ('name')

class RockTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RockType
        fields = '__all__'


class MineralSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Mineral
        fields = '__all__'


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
    owner = serializers.ReadOnlyField(source='owner.name')
    rock_type = serializers.ReadOnlyField(source='rock_type.name')
    metamorphic_grades = serializers.SerializerMethodField(read_only=True)
    metamorphic_regions = serializers.SerializerMethodField(read_only=True)
    minerals = serializers.SerializerMethodField(read_only=True)
    references = serializers.SerializerMethodField(read_only=True)
    latitude = serializers.SerializerMethodField(read_only=True)
    longitude = serializers.SerializerMethodField(read_only=True)
    # collection_date = serializers.SerializerMethodField(read_only=True)

    images = ImageSerializer(many=True, read_only=True)

    # TODO: figure out if there is a better, more efficient way to do this
    subsample_ids = serializers.SerializerMethodField()
    chemical_analyses_ids = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        depth = 1
        fields = SAMPLE_FIELDS

    def is_valid(self, raise_exception=False):
        if self.initial_data.get('latitude') and self.initial_data.get('longitude'):
            self.initial_data['location_coords'] = "SRID=4326;POINT ("+str(self.initial_data["longitude"])+" "+str(self.initial_data["latitude"])+")"
            
        super().is_valid(raise_exception)

        self._validated_data.update({'location_coords':self.initial_data['location_coords']})

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
            # if attr in SAMPLE_FIELDS:
                setattr(instance, attr, value)
        instance.save()

        return instance

    def get_metamorphic_grades(self,obj):
        return [g.name for g in obj.metamorphic_grades.all()]

    def get_metamorphic_regions(self,obj):
        return [r.name for r in obj.metamorphic_regions.all()]

    def get_minerals(self,obj):
        return [m.mineral.name for m in obj.samplemineral_set.all()]

    def get_references(self,obj):
        return [r.name for r in obj.references.all()]

    def get_longitude(self,obj):
        return round(obj.location_coords[0],5)

    def get_latitude(self,obj):
        return round(obj.location_coords[1],5)

    def get_collection_date(self,obj):
        # print(obj.collection_date)
        date = str(obj.collection_date).split(' ')[0]
        return '' if date == 'None' else date

    def get_subsample_ids(self, obj):
        return Subsample.objects.filter(sample_id=obj.pk).values_list('id', flat=True)

    def get_chemical_analyses_ids(self, obj):
        subsample_ids = obj.subsamples.values_list('id', flat=True)
        return ChemicalAnalysis.objects.filter(
            subsample_id__in=subsample_ids).values_list('id', flat=True)


class SubsampleSerializer(DynamicFieldsModelSerializer):
    sample = SampleSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subsample
        depth = 1
        fields = '__all__'

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
        fields = '__all__'


class MetamorphicGradeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicGrade
        fields = '__all__'


class MetamorphicRegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicRegion
        fields = '__all__'


class GeoReferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = GeoReference
        fields = '__all__'


class RegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class ReferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'


class CollectorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Collector
        fields = '__all__'