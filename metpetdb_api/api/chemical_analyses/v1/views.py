from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from api.chemical_analyses.v1.renderers import ChemicalAnalysisCSVRenderer

from api.chemical_analyses.lib.query import chemical_analysis_query
from api.chemical_analyses.v1.serializers import (
    ChemicalAnalysisSerializer,
    ElementSerializer,
    OxideSerializer,
)

from api.lib.permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly
from api.lib.query import sample_qs_optimizer, chemical_analyses_qs_optimizer
from api.samples.lib.query import sample_query

from apps.samples.models import Sample, Mineral, Subsample
from apps.chemical_analyses.models import (
    ChemicalAnalysis,
    ChemicalAnalysisElement,
    ChemicalAnalysisOxide,
    Element,
    Oxide,
)


class ChemicalAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ChemicalAnalysis.objects.all()
    serializer_class = ChemicalAnalysisSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, ChemicalAnalysisCSVRenderer)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'PUT':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if params.get('sample_filters') == 'True':
            sample_qs = Sample.objects.all()
            sample_qs = sample_qs_optimizer(params, sample_qs)
            sample_ids = sample_query(request.user,
                                      params,
                                      sample_qs).values_list('id')
            qs = ChemicalAnalysis.objects.filter(
                subsample__sample_id__in=sample_ids)
        else:
            qs = self.get_queryset().distinct()
            qs = chemical_analysis_query(request.user, params, qs)

        qs = chemical_analyses_qs_optimizer(params, qs)

        if params.get('format') == 'csv':
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)


    def _handle_elements(self, instance, params):
        to_add = []
        for record in params['elements']:
            try:
                to_add.append({
                    'element': Element.objects.get(pk=record['id']),
                    'amount': record['amount'],
                    'precision': record['precision'],
                    'precision_type': record['precision_type'],
                    'measurement_unit': record['measurement_unit'],
                    'min_amount': record['min_amount'],
                    'max_amount': record['max_amount']
                })
            except Element.DoesNotExist:
                return Response(
                    data={'error': 'Invalid element id'},
                    status=400)

        (ChemicalAnalysisElement
         .objects
         .filter(chemical_analysis=instance)
         .delete())

        for record in to_add:
            ChemicalAnalysisElement.objects.create(
                chemical_analysis=instance,
                element=record['element'],
                amount=record['amount'],
                precision=record['precision'],
                precision_type=record['precision_type'],
                measurement_unit=record['measurement_unit'],
                min_amount=record['min_amount'],
                max_amount=record['max_amount']
            )


    def _handle_oxides(self, instance, params):
        to_add = []
        for record in params['oxides']:
            try:
                to_add.append({
                    'oxide': Oxide.objects.get(pk=record['id']),
                    'amount': record['amount'],
                    'precision': record['precision'],
                    'precision_type': record['precision_type'],
                    'measurement_unit': record['measurement_unit'],
                    'min_amount': record['min_amount'],
                    'max_amount': record['max_amount']
                })
            except Oxide.DoesNotExist:
                return Response(
                    data={'error': 'Invalid oxide id'},
                    status=400)

        (ChemicalAnalysisOxide
         .objects
         .filter(chemical_analysis=instance)
         .delete())

        for record in to_add:
            ChemicalAnalysisOxide.objects.create(
                chemical_analysis=instance,
                oxide=record['oxide'],
                amount=record['amount'],
                precision=record['precision'],
                precision_type=record['precision_type'],
                measurement_unit=record['measurement_unit'],
                min_amount=record['min_amount'],
                max_amount=record['max_amount']
            )


    def perform_create(self, serializer):
        return serializer.save()


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        if request.data.get('elements'):
            for record in request.data.get('elements'):
                try:
                    ChemicalAnalysisElement.objects.create(
                        chemical_analysis=instance,
                        element=Element.objects.get(pk=record['id']),
                        amount=record['amount'],
                        precision=record['precision'],
                        precision_type=record['precision_type'],
                        measurement_unit=record['measurement_unit'],
                        min_amount=record['min_amount'],
                        max_amount=record['max_amount'],
                    )
                except Element.DoesNotExist:
                    return Response(data={'error': 'Invalid element id'},
                                    status=400)

        if request.data.get('oxides'):
            for record in request.data.get('oxides'):
                try:
                    ChemicalAnalysisOxide.objects.create(
                        chemical_analysis=instance,
                        oxide=Oxide.objects.get(pk=record['id']),
                        amount=record['amount'],
                        precision=record['precision'],
                        precision_type=record['precision_type'],
                        measurement_unit=record['measurement_unit'],
                        min_amount=record['min_amount'],
                        max_amount=record['max_amount'],
                    )
                except Oxide.DoesNotExist:
                    return Response(data={'error': 'Invalid oxide id'},
                                    status=400)

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

        if 'mineral_id' in params:
            try:
                mineral = Mineral.objects.get(pk=params['mineral_id'])
            except Mineral.DoesNotExist:
                return Response(data={'error': 'Invalid mineral id'},
                                status=400)
            else:
                instance.mineral = mineral

        if 'subsample_id' in params:
            try:
                subsample = Subsample.objects.get(pk=params['subsample_id'])
            except Mineral.DoesNotExist:
                return Response(data={'error': 'Invalid subsample id'},
                                status=400)
            else:
                instance.subsample = subsample

        if 'elements' in params:
            self._handle_elements(instance, params)

        if 'oxides' in params:
            self._handle_oxides(instance, params)

        instance.save()
        # refresh the data before returning a response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class OxideViewSet(viewsets.ModelViewSet):
    queryset = Oxide.objects.all()
    serializer_class = OxideSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)
