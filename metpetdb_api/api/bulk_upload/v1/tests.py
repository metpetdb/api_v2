import json
from rest_framework import status
from rest_framework.test import APIClient, APITransactionTestCase

from apps.users.models import User

from apps.samples.models import (
    Mineral,
    RockType,
    Sample,
    SubsampleType,
    Subsample
)

from apps.chemical_analyses.shared_models import Element, Oxide


class BulkUploadTests(APITransactionTestCase):
    """
    Bulk upload error classes are documented in the wiki: 
    https://github.com/metpetdb/api_v2/wiki/Bulk-Upload

    Note that these tests rely on files uploaded to DropBox.
    An internet connection is required for most of them to pass.
    """
    def setUp(self):
        #Create a user
        self.contributor1=User.objects.create_user(
            email='contributor1@metpetb.com',
            password='contributor1',
            is_active=True
        )

        self.owner=self.contributor1.id     
        
        #Authenticate User
        self.client=APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.contributor1.auth_token.key
        )
 
        #Create required minerals
        minerals=['Silica', 'Quartz', 'Mica', 'Kalsilite', 'Celsian', 'Leucite']
        Mineral.objects.bulk_create([Mineral(name=n) for n in minerals])

        #Create required rock type
        rock_type=RockType.objects.create(name='Slate')

        #Create required elements
        elements=[{'name': 'Argon', 'atomic_number' : 18, 'symbol' : 'Ar'},
                  {'name': 'Silver', 'atomic_number': 47, 'symbol': 'Ag'}]
        self.elements=Element.objects.bulk_create([Element(**n) for n in elements])

        #Create required Oxides
        Oxide.objects.create(species='FeO', conversion_factor=1.28659683051303, element_id=self.elements[0].id)

        #Create required Subsample
        sample=Sample.objects.create(rock_type=rock_type, location_coords='POINT(-95.3385 29.7245)', owner_id=self.owner)
        subsample_type=SubsampleType.objects.create(name='Rock Chip')
        Subsample.objects.create(id='dfab518c-7876-4d8d-ab62-22a4b2fb0cc4', owner=self.contributor1, 
                                 sample=sample, subsample_type=subsample_type)

    def empty_errors(self, lst):
        """
        Returns true iff lst contains fields with no errors
        """
        return all(len(x['errors'])==0 for x in lst if 'errors' in x.keys())

    def is_error(self,lst,err):
        """
        Returns true iff err is an error in at least one object in lst
        """
        for l in lst:
            if l['errors'] and err in l['errors'].values():
                    return True
        return False 

    def field_has_multiple_errors(self,lst):
        """
        Returns true iff lst contains an object with more than one error
        """
        for l in lst:
            if l['errors'] and len(l['errors']) > 1:
                return True
        return False

    def test_bulkupload_samples_no_errors(self):
        """
        Errorless sample bulk upload
        """
        data={'owner' : self.owner, 
              'template' : 'SampleTemplate',
              'url' : 'https://www.dropbox.com/s/2w7tav2bmdag72t/sample-redo-dates.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)
        self.assertTrue(self.empty_errors(res.data))

    def test_bulkupload_chemical_analyses_no_errors(self):
        """
        Errorless chemical analyses bulk upload
        """
        data={ 'owner' : self.owner,
               'template' : 'ChemicalAnalysesTemplate',
               'url' : 'https://www.dropbox.com/s/cyna912h69ylov8/chem-a-updated.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)       
        self.assertTrue(self.empty_errors(res.data))

    def test_invalid_bulkupload_template(self):
        """
        Non-existent bulkupload_template
        """
        data={'owner' : self.owner,
              'template' : 'NoExistTemplate',
              'url' : 'https://www.dropbox.com/s/2w7tav2bmdag72t/sample-redo-dates.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['error'], 'invalid template')

    def test_sample_missing_required_field(self):
        """
        Missing required field in sample
        """
        data={'owner' : self.owner,
              'template': 'SampleTemplate',
              'url' : 'https://www.dropbox.com/s/qw8nv3lwgn2c95l/sample_miss_no.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.is_error(res.data,'missing'))

    def test_chemical_analysis_missing_required_field(self):
        """
        Missing required field in chemical analysis
        """
        data={'owner' : self.owner,
              'template' : 'ChemicalAnalysesTemplate',
              'url' : 'https://www.dropbox.com/s/ylvw8gslwby5dbq/chem-a-miss-id.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.is_error(res.data,'missing'))

    def test_sample_invalid_required_type(self):
        """
        Create a sample with an invalid required type
        """
        data={'owner' : self.owner,
              'template': 'SampleTemplate',
              'url' : 'https://www.dropbox.com/s/mibznbi5d4o8616/sample-invalid-latitude.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.is_error(res.data,'float expected'))


    def test_chemical_analysis_invalid_required_type(self):
        """
        Create a chemical analysis with an invalid required type
        """	
        data={'owner' : self.owner,
              'template' : 'ChemicalAnalysesTemplate',
              'url' : 'https://www.dropbox.com/s/hgm1dfmi2aezx40/chem-a-type-err.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.is_error(res.data,'float expected'))

    def test_sample_multi_error(self):
        """
        Submit a samples csv with multiple soft errors
        """
        data={'owner' : self.owner,
              'template' : 'SampleTemplate',
              'url' : 'https://www.dropbox.com/s/k3y6dily50tue16/sample-multiple-error.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.field_has_multiple_errors(res.data))

    def test_chemical_analysis_multi_error(self):
        """
        Submit a chemical analysis csv with multiple soft errors
        """
        data={'owner' : self.owner,
              'template' : 'ChemicalAnalysesTemplate',
              'url' : 'https://www.dropbox.com/s/uubppw4tzjszfm7/chem-a-comb-err.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))
        self.assertTrue(self.field_has_multiple_errors(res.data))

    def test_db_error(self):
        """
        Submit a csv with a reference to an invalid foreign key 
        """
        data={'owner' : self.owner,
              'template': 'ChemicalAnalysesTemplate',
              'url' : 'https://www.dropbox.com/s/zol737s9uxa0xtr/chem-a-invalid-subsample-id.csv?dl=0'}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.empty_errors(res.data))

    def test_sample_json_fix(self):
        data={'owner' : self.owner,
              'template' : 'SampleTemplate',
              'json': [{"location_name":"The U S of A","mineral":[{"amount":0,"name":"Silica"},{"amount":0,"name":"Quartz"},{"amount":0,"name":"Mica"}],"number":"1","country":"USA","comment":["Comment on the sample"],"collection_date":"1999-03-27","region":"Troy","description":"Uber Sample","alias":"2","rock_type_name":"Slate","collector_name":"Brandon D.","location_error":"7","latitude":"7.86210012","longitude":"46.01432423","errors":{},"metamorpic_grade":"Chlorite Zone","reference":"2000-038151"},{"location_name":"Merica","mineral":[{"amount":0,"name":"Silica"},{"amount":0,"name":"Quartz"},{"amount":0,"name":"Mica"}],"number":"7","country":"USA","comment":["Comment on the sample2"],"collection_date":"1999-03-22","region":"Boston","description":"Cool Sample","alias":"2213","rock_type_name":"Slate","collector_name":"Brandon P.","location_error":"2","latitude":"12.86210012","longitude":"13.01432423","errors":{"number":"missing"},"metamorpic_grade":"Biotite Zone","reference":"2000-038151"},{"meta_header":[["number","number"],["alias","alias"],["region","region"],["country","country"],[["latitude","longitude"],"location_coords"],["collector_name","collector_name"],["collection_date","collection_date"],["comment","comment"],["location_name","location_name"],["rock_type_name","rock_type_name"],["reference","reference"],["description","description"],["metamorpic_grade","metamorpic_grade"],["mineral","minerals"]]}]}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_chemical_analysis_json_fix(self):
        data={'owner' : self.owner,
              'template' : 'ChemicalAnalysesTemplate',
              'json': [{"analysis_date":"1990-03-12","mineral":[{"name":"Kalsilite","amount":"4"}],"stage_y":2.0,"analyst":"7","analysis_method":"4","reference_image":"8","stage_x":1.0,"where_done":"5","subsample_id":"dfab518c-7876-4d8d-ab62-22a4b2fb0cc4","reference_x":9.0," reference_y":"0","total":"3","element":[{"name":"Argon","amount":"2"}],"spot_id":"2","errors":{},"amount":"3","oxide":[{"name":"FeO","amount":"3"}],"comment":["1","2","3"]},{"analysis_date":"1990-03-12","mineral":[{"name":"Celsian","amount":"4"}],"stage_y":2.0,"analyst":"7","analysis_method":"4","reference_image":"8","stage_x":1.0,"where_done":"5","subsample_id":"dfab518c-7876-4d8d-ab62-22a4b2fb0cc4","reference_x":9.0," reference_y":"0","total":"3","element":[{"name":"Argon","amount":"3"}],"spot_id":"2","errors":{},"amount":"6","oxide":[{"name":"FeO","amount":"6"}],"comment":["1","2","3"]},{"analysis_date":"1990-03-12","mineral":[{"name":"Leucite","amount":"4"}],"stage_y":2.0,"analyst":"7","analysis_method":"4","reference_image":"8","stage_x":1.0,"where_done":"5","subsample_id":"dfab518c-7876-4d8d-ab62-22a4b2fb0cc4","reference_x":9.0," reference_y":"0","total":"3","element":[{"name":"Silver","amount":"5"}],"spot_id":"2","errors":{},"amount":"9","oxide":[{"name":"FeO","amount":"9"}],"comment":["6","7","8"]},{"meta_header":[["subsample_id","subsample_id"],["spot_id","spot_id"],["mineral","mineral"],["analysis_method","analysis_method"],["where_done","where_done"],["analysis_date","analysis_date"],["analyst","analyst"],["reference_image","reference_image"],["reference_x","reference_x"],[" reference_y"," reference_y"],["stage_x","stage_x"],["stage_y","stage_y"],["total","total"],["element","element"],["amount","amount"],["oxide","oxide"],["amount","amount"],["comment","comment"],["comment","comment"],["comment","comment"]]}]}
        res=self.client.post('/api/bulk_upload/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

