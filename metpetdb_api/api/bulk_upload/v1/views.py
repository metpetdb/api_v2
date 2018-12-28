from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

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

from api.chemical_analyses.lib.query import chemical_analysis_query
from api.chemical_analyses.v1.serializers import (
    ChemicalAnalysisSerializer,
    ElementSerializer,
    OxideSerializer,
)

from api.lib.permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly
from api.lib.query import sample_qs_optimizer, chemical_analyses_qs_optimizer
from api.samples.lib.query import sample_query

from apps.samples.models import Sample, Mineral, Subsample, BulkUpload
from apps.chemical_analyses.models import (
    ChemicalAnalysis,
    ChemicalAnalysisElement,
    ChemicalAnalysisOxide,
)
from apps.chemical_analyses.shared_models import Element, Oxide

from api.bulk_upload.v1 import upload_templates
import json
import sys
import urllib.request
from csv import reader


sample_labels_dict = {
    'Sample Number':'number',
    'Rock Type':'rock_type_name',
    'Latitude':'latitude',
    'Longitude':'longitude',
    'Location Error':'location_error',
    'Collector':'collector_name',
    'Date of Collection':'collection_date',
    'Present Sample Location':'location_name',
    'Country':'country'
}


class Parser:
    def __init__(self, template):
        self.template = template 
    
    def line_split(self, content):
        data = content.decode('utf-8').split('\r\n')
        if len(data) < 2: data = content.decode('utf-8').split('\n')
        if len(data) < 2: raise ValueError('No data entries')
        lined = [] # line separated data
        for entry in reader(data): lined.append(entry)
        return lined

    # Effects: Generates JSON file from passed template
    def parse(self, url):   
        try:
            url = url[:-1] +'1' # specific to dropBox urls
            content = urllib.request.urlopen(url).read()
            lined = self.line_split(content)
            return  self.template.parse(lined) # return the JSON ready file
        except Exception as err:
            print(err)
            raise ValueError(str(err))

class BulkUploadViewSet(viewsets.ModelViewSet):
    queryset = BulkUpload.objects.none()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    http_method_names=['post'] 

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


    def _handle_metamorphic_grades(self, instance, grades):
        metamorphic_grades = []
        for grade in grades:
            try:
                metamorphic_grade = MetamorphicGrade.objects.get(name=grade)
            except:
                raise ValueError('Invalid metamorphic_grade : {}'.format(grade))
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

        instance.references.clear()
        instance.references.add(*to_add)


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

    
    def rollback_transaction(self):
        transaction.rollback()
        transaction.set_autocommit(True)

    def set_err(self, JSON, i, field, val, meta_header):
        self.rollback_transaction()
        JSON[i]['errors'][field] = val
        JSON.append({"meta_header": meta_header})   
        return Response(
            data = JSON,
            status = 400
        )
    
    def parse_chemical_analyses(self, request, JSON, meta_header):
        before_parse_json = list(JSON)
        
        # Manual transaction for ease of exception handling
        transaction.set_autocommit(False)
        
        for i,chemical_analyses_obj in enumerate(JSON):
            try:
                chemical_analyses_obj['owner'] = request.data.get('owner')    
            except:
                self.rollback_transaction()
                return Response(
                    data = {'error': 'missing owner in header'},
                    status = 400
                )

            #fix date formatting
            if chemical_analyses_obj['analysis_date']:
                chemical_analyses_obj['analysis_date'] += 'T00:00:00.000Z'

            try:
                chemical_analyses_obj['mineral_id'] = Mineral.objects.get(name=chemical_analyses_obj['mineral'][0]['name']).id
            
            except Exception as err:
                return self.set_err(before_parse_json, i, 'mineral_id', 'invalid mineral', meta_header)           

            elements_to_add = []
            for element in chemical_analyses_obj['element']:
                try:
                    elements_to_add.append(
                        {'id': Element.objects.get(name=element['name']).id,
                         'amount': element['amount'],
                         #TODO consider adding these fields
                         #They are not specified in the template
                         'precision': None, 
                         'precision_type':  None,
                         'measurement_unit': None, 
                         'min_amount': None, 
                         'max_amount': None 
                        })
                except:
                    return self.set_err(before_parse_json, i, 'element', 'invalid element {0}'.format(element), meta_header)

            chemical_analyses_obj['elements'] = elements_to_add

            oxides_to_add = []

            for oxide in chemical_analyses_obj['oxide']:
                try:
                    oxides_to_add.append(
                        {   'id' : Oxide.objects.get(species=oxide['name']).id,
                            'amount': oxide['amount'],
                            #TODO consider adding
                            #They are currently not specified in the template
                            'precision': None, 
                            'precision_type': None,
                            'measurement_unit': None,
                            'min_amount': None,
                            'max_amount': None

                        })
                except:
                    return self.set_err(before_parse_json, i, 'oxide', 'invalid oxide {0}'.format(oxide), meta_header)
                            
            chemical_analyses_obj['oxides'] = oxides_to_add    

            serializer = self.get_serializer(data=chemical_analyses_obj)
            try:
                serializer.is_valid(raise_exception=True)
                instance = self.perform_create(serializer)
            except Exception as e:
                return self.set_err(before_parse_json, i, 'serialization', str(e), meta_header)
            

            if chemical_analyses_obj.get('elements'):
                for record in chemical_analyses_obj.get('elements'):
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
                        return self.set_err(before_parse_json, i, 'elements', 'invalid element id', meta_header)

            if chemical_analyses_obj.get('oxides'):
                for record in chemical_analyses_obj.get('oxides'):
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
                        return self.set_err(before_parse_json, i, 'oxides', 'invalid oxide id', meta_header)

        headers = self.get_success_headers(serializer.data)
        JSON.append({"meta_header": meta_header})
        
        transaction.commit()
        transaction.set_autocommit(True)
        
        return Response(JSON,
                        status=status.HTTP_201_CREATED,
                        headers=headers)
    
    def parse_samples(self, request, JSON, meta_header):
        before_parse_json = list(JSON)

        # Set transactions manually to allow for ease of exception handling
        transaction.set_autocommit(False)

        for i,sample_obj in enumerate(JSON):

            print(sample_obj)

            # REQUIRED FIELDS:
            #   Sample Number
            #   Rock Type
            #   Latitude
            #   Longitude

            # OPTIONAL FIELDS:
            #   Location Error
            #   Metamorphic Region
            #   Reference
            #   Present Sample Location
            #   Region
            #   Date of Collection
            #   Comment
            #   Metamorphic Grade
            #   Country
            #   Collector
            #   [minerals]


            # PROCEDURE:
            ## ensure all required fields are present
            ## verify all other fields are valid optional fields or minerals
            ## manipulate data for serializer
            ## create serializer

            minerals = []
            fields = [x for x in sample_obj.keys()]
            for field in fields:
                if field.lower() in upload_templates.sample_label_mappings.keys():
                    # add proper formatting to date
                    if field.lower() == 'date of collection':
                        sample_obj[field] = sample_obj[field] + 'T00:00:00.000Z'
                    # join comments with newline
                    elif field.lower() == 'comment':
                        sample_obj[field] = '\n'.join(sample_obj[field])
                    # replace field with corresponding serializer fieldname
                    sample_obj[upload_templates.sample_label_mappings[field.lower()]] = sample_obj[field]
                    del(sample_obj[field])
                elif field != 'errors' and field not in upload_templates.sample_label_mappings.values(): # it had better be a mineral
                    try: 
                        amount = sample_obj[field]
                        minerals.append(
                            {'id':Mineral.objects.get(name=field).id,
                             'name':field,
                             'amount':amount})
                    except:
                        print(field)
                        return self.set_err(before_parse_json, i, 'minerals', 'Invalid mineral {}'.format(field), meta_header)

            sample_obj['minerals'] = minerals

            try:
                sample_obj['owner'] = request.data.get('owner')
            except:
                self.rollback_transaction() 
                return Response(
                    data = {'error' : 'Missing owner in header'},
                    status = 400
                )

            if 'latitude' in sample_obj.keys() and 'longitude' in sample_obj.keys():
                sample_obj['location_coords'] =  u'SRID=4326;POINT ({0} {1})'.format(sample_obj['latitude'], sample_obj['longitude'])
                del(sample_obj['latitude'])
                del(sample_obj['longitude'])

            rock_type = sample_obj['rock_type_name']
            try:
                sample_obj['rock_type_id'] = RockType.objects.get(name=rock_type).id
            except:
                return self.set_err(before_parse_json, i, 'rock_type_id', 'Invalid rock {0}'.format(rock_type), meta_header)
            
            
            
            serializer = self.get_serializer(data=sample_obj)
            try:
                serializer.is_valid(raise_exception=True)
                instance = self.perform_create(serializer)
            except Exception as e:
                return self.set_err(before_parse_json, i, 'serialization', str(e), meta_header)
        
        
            metamorphic_region_ids = sample_obj.get('metamorphic_region_id')
            metamorphic_grades = sample_obj.get('metamorphic_grade')           
            references = sample_obj.get('references')
            minerals = sample_obj.get('minerals')

            if metamorphic_region_ids:
                try:
                    self._handle_metamorphic_regions(instance,
                                                     metamorphic_region_ids)
                except ValueError as err:
                    return self.set_err(before_parse_json, i, 'metamorphic_region_ids', err.args, meta_header)

            if metamorphic_grades:
                try:
                    self._handle_metamorphic_grades(instance,
                                                    metamorphic_grades)
                except ValueError as err:
                    return self.set_err(before_parse_json, i, 'metamorphic_grades', err.args, meta_header)
            
            if minerals:
                try:
                    self._handle_minerals(instance,minerals)
                except ValueError as err:
                    return self.set_err(before_parse_json, i, 'minerals', err.args, meta_header)

            if references:
                self._handle_references(instance, references)

        JSON.append({"meta_header": meta_header})    
        headers = self.get_success_headers(serializer.data)
        
        transaction.commit()
        transaction.set_autocommit(True)
        
        return Response(JSON,
                        status=status.HTTP_201_CREATED,
                        headers=headers)       

    def create(self, request, *args, **kwargs):
        url = request.data.get('url')
        JSON = request.data.get('json')
        template_name = request.data.get('template')
        template_instance = ''

        #Dynamically generate instance of template
        try:
            module = upload_templates
            class_ = getattr(module, template_name)
            template_instance = class_()
        except:
            return Response(
                data = {'error': 'invalid template'},
                status=400
            )

        #JSON received, update accordingly
        if JSON:
            meta_header = JSON[-1]['meta_header']
            del JSON[-1]
            # clear out the old errors
            for obj in JSON:
                obj['errors'] = {}
            # TODO perform simple verification of fields for template type      
            try:
                pass
                # p = Parser(template_instance)
                # p. verify correctness
            except Exception as err:
                return Response(
                    data = {'error': str(err)},
                    status = 400
                )
        
        # Parse the input for basic errors
        # These are errors that are catchable without the data model
        else:
            try: 
                p = Parser(template_instance)
                JSON,meta_header = p.parse(url)

            except Exception as err:
                return Response(
                    data = {'error': str(err)},
                    status = 400
                )
  
        for obj in JSON:
            if len(obj['errors']) > 0:
                JSON.append({"meta_header": meta_header})
                return Response(JSON,
                                status=400)
        
        if template_name == 'SampleTemplate':
            self.serializer_class = SampleSerializer
            return self.parse_samples(request, JSON, meta_header)

        elif template_name == 'ChemicalAnalysesTemplate':
            self.serializer_class = ChemicalAnalysisSerializer
            return self.parse_chemical_analyses(request,JSON, meta_header)

        else:
            return Response(
                data = {'error': 'invalid template'},
                status = 400
            )


class SubsampleViewSet(viewsets.ModelViewSet):
    queryset = Subsample.objects.all()
    serializer_class = SubsampleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


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
    queryset = MetamorphicRegion.objects.all()
    serializer_class = MetamorphicRegionSerializer
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
