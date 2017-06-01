from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.chemical_analyses.lib.query import chemical_analysis_query
from api.lib.permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly
from api.lib.query import sample_qs_optimizer, chemical_analyses_qs_optimizer

from api.samples.lib.query import sample_query
from api.samples.v1.serializers import (
    SampleSerializer,
    RockTypeSerializer,
    MineralSerializer,
    RegionSerializer,
    ReferenceSerializer,
    CollectorSerializer,
    SubsampleSerializer,
    MetamorphicRegionSerializer,
    MetamorphicGradeSerializer,
    GeoReferenceSerializer,
    SubsampleTypeSerializer,
)
from apps.chemical_analyses.models import ChemicalAnalysis
from apps.samples.models import (
    Country,
    Sample,
    RockType,
    Mineral,
    Region,
    Reference,
    Collector,
    Subsample,
    MetamorphicRegion,
    MetamorphicGrade,
    SampleMineral,
    GeoReference,
    SubsampleType,
)


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'PUT':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)


    def list(self, request, *args, **kwargs):
        params = request.query_params

        if params.get('chemical_analyses_filters') == 'True':
            chem_qs = ChemicalAnalysis.objects.all()
            chem_qs = chemical_analyses_qs_optimizer(params, chem_qs)
            chem_ids = (chemical_analysis_query(request.user, params, chem_qs)
                        .values_list('id'))
            qs = (Sample
                  .objects
                  .filter(subsamples__chemical_analyses__id__in=chem_ids))
        else:
            qs = self.get_queryset().distinct()
            try:
                qs = sample_query(request.user, params, qs)
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        qs = sample_qs_optimizer(params, qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


    def _handle_metamorphic_regions(self, instance, ids):
        metamorphic_regions = []
        for id in ids:
            try:
                metamorphic_region = MetamorphicRegion.objects.get(pk=id)
            except:
                raise ValueError('Invalid metamorphic_region id: {}'
                                 .format(id))
            else:
                metamorphic_regions.append(metamorphic_region)
        instance.metamorphic_regions = metamorphic_regions


    def _handle_metamorphic_grades(self, instance, ids):
        metamorphic_grades = []
        for id in ids:
            try:
                metamorphic_grade = MetamorphicGrade.objects.get(pk=id)
            except:
                raise ValueError('Invalid metamorphic_grade id: {}'.format(id))
            else:
                metamorphic_grades.append(metamorphic_grade)
        instance.metamorphic_grades = metamorphic_grades


    def _handle_minerals(self, instance, minerals):
        to_add = []
        for record in minerals:
            try:
                to_add.append(
                    {'mineral': Mineral.objects.get(pk=record['id']),
                     'amount': record['amount']})
            except Mineral.DoesNotExist:
                raise ValueError('Invalid mineral id: {}'.format(record['id']))

        SampleMineral.objects.filter(sample=instance).delete()
        for record in to_add:
            SampleMineral.objects.create(sample=instance,
                                         mineral=record['mineral'],
                                         amount=record['amount'])


    def _handle_references(self, instance, references):
        to_add = []

        georefences = GeoReference.objects.filter(name__in=references)
        to_add.extend(georefences)

        missing_georefs = (set(references) -
                           set([georef.name for georef in georefences]))
        if missing_georefs:
            new_georefs = GeoReference.objects.bulk_create(
                [GeoReference(name=name) for name in missing_georefs]
            )
            Reference.objects.bulk_create([Reference(name=name)
                                           for name in missing_georefs])
            to_add.extend(new_georefs)

        # FIXME: this is lazy; we should ideally clear only those
        # associations that aren't needed anymore and create new
        # associations, if required.
        instance.references.clear()
        instance.references.add(*to_add)


    def perform_create(self, serializer):
        return serializer.save()


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        metamorphic_region_ids = request.data.get('metamorphic_region_ids')
        metamorphic_grade_ids = request.data.get('metamorphic_grade_ids')
        minerals = request.data.get('minerals')
        references = request.data.get('references')

        if metamorphic_region_ids:
            try:
                self._handle_metamorphic_regions(instance,
                                                 metamorphic_region_ids)
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if metamorphic_grade_ids:
            try:
                self._handle_metamorphic_grades(instance,
                                                metamorphic_grade_ids)
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if minerals:
            try:
                self._handle_minerals(instance, minerals)
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if references:
            self._handle_references(instance, references)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


    def update(self, request, *args, **kwargs):
        params = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if 'rock_type_id' in params:
            try:
                rock_type = RockType.objects.get(pk=params['rock_type_id'])
            except RockType.DoesNotExist:
                return Response(data={'error': 'Invalid rock_type id'},
                                status=400)
            else:
                instance.rock_type = rock_type

        if 'metamorphic_region_ids' in params:
            try:
                self._handle_metamorphic_regions(
                    instance,
                    params['metamorphic_region_ids']
                )
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if 'metamorphic_grade_ids' in params:
            try:
                self._handle_metamorphic_grades(
                    instance,
                    params['metamorphic_grade_ids']
                )
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if 'minerals' in params:
            try:
                self._handle_minerals(instance, params['minerals'])
            except ValueError as err:
                return Response(
                    data={'error': err.args},
                    status=400
                )

        if 'references' in params:
            self._handle_references(instance, params['references'])

        instance.save()
        # refresh the data before returning a response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SubsampleViewSet(viewsets.ModelViewSet):
    queryset = Subsample.objects.all()
    serializer_class = SubsampleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'PUT':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)


    def list(self, request, *args, **kwargs):
        
        params = request.query_params

        qs = self.get_queryset().distinct()
        
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
      
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        params = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if 'sample' in params:
            try:
                sample = Sample.objects.get(pk=params['sample'])
            except Sample.DoesNotExist:
                return Response(data={'error': 'Invalid sample id'},
                                status=400)
            else:
                instance.sample = sample

        if 'subsample_type' in params:
            try:
                subsample_type = SubsampleType.objects.get(pk=params['subsample_type'])
            except SubsampleType.DoesNotExist:
                return Response(data={'error': 'Invalid subsample type'},
                                status=400)
            else:
                instance.subsample_type = subsample_type     

        instance.save()
        # refresh the data before returning a response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    

class SubsampleTypeViewSet(viewsets.ModelViewSet):
    queryset = SubsampleType.objects.all()
    serializer_class = SubsampleTypeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class RockTypeViewSet(viewsets.ModelViewSet):
    queryset = RockType.objects.all()
    serializer_class = RockTypeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class MineralViewSet(viewsets.ModelViewSet):
    queryset = Mineral.objects.all()
    serializer_class = MineralSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class MetamorphicRegionViewSet(viewsets.ModelViewSet):
    queryset = MetamorphicRegion.objects.all()
    serializer_class = MetamorphicRegionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class MetamorphicGradeViewSet(viewsets.ModelViewSet):
    queryset = MetamorphicGrade.objects.all()
    serializer_class = MetamorphicGradeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class GeoReferenceViewSet(viewsets.ModelViewSet):
    queryset = GeoReference.objects.all()
    serializer_class = GeoReferenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class SampleNumbersView(APIView):
    def get(self, request, format=None):
        sample_numbers = (
            Sample
            .objects
            .all()
            .values_list('number', flat=True)
            .distinct()
        )
        return Response({'sample_numbers': sample_numbers})


class CountryNamesView(APIView):
    def get(self, request, format=None):
        country_names = (
            Country
            .objects
            .all()
            .values_list('name', flat=True)
            .distinct()
        )
        return Response({'country_names': country_names})


class SampleOwnerNamesView(APIView):
    def get(self, request, format=None):
        sample_owner_names = (
            Sample
            .objects
            .all()
            .values_list('owner__name', flat=True)
            .distinct()
        )
        return Response({'sample_owner_names': sample_owner_names})
