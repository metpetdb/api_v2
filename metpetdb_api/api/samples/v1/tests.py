import json
import random
from copy import deepcopy

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.samples.models import (
    GeoReference,
    MetamorphicGrade,
    MetamorphicRegion,
    Mineral,
    RockType,
)
from apps.users.models import User


def get_random_str(length=10):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz')
                   for x in range(length))


class SampleTests(APITestCase):

    def setUp(self):
        self.contributor1 = User.objects.create_user(
            email='contributor1@metpetb.com',
            password='contributor1',
            is_active=True
        )
        self.superuser1 = User.objects.create_superuser(
            email='superuser1@metpetb.com',
            password='superuser1',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            email='inactive@metpetdb.com'
        )

        self.rock_type = RockType.objects.create(name=get_random_str())
        self.metamorphic_grades= MetamorphicGrade.objects.bulk_create(
            [MetamorphicGrade(name=get_random_str()) for i in range(5)]
        )

        self.metamorphic_regions = MetamorphicRegion.objects.bulk_create(
            [MetamorphicRegion(name=get_random_str(),
                               description=get_random_str())
             for i in range(5)]
        )

        self.georeferences = GeoReference.objects.bulk_create(
            [GeoReference(name=get_random_str(),
                          title=get_random_str(70))
             for i in range(5)]
        )

        self.minerals = Mineral.objects.bulk_create(
            [Mineral(name=get_random_str()) for i in range(5)]
        )
        some_more_minerals = Mineral.objects.bulk_create(
            [Mineral(name=get_random_str(),
                     real_mineral=self.minerals[i])
             for i in range(5)]
        )
        self.minerals.extend(some_more_minerals)

        regions = [get_random_str() for i in range(5)]
        countries = [get_random_str() for i in range(5)]

        self.sample_data = dict(
            number=get_random_str(),
            rock_type_id=str(self.rock_type.pk),
            aliases=[get_random_str() for i in range(5)],
            description=get_random_str(40),
            location_coords="SRID=4326;POINT (-118.4008865356450002 "
                            "49.1695137023925994)",
            minerals=[
                {
                    "id": str(self.minerals[0].pk),
                    "amount": "x",
                },
                {
                    "id": str(self.minerals[1].pk),
                    "amount": "x",
                },
            ],
            metamorphic_grade_ids=[str(mg.pk)
                                   for mg in self.metamorphic_grades],
            metamorphic_region_ids=[str(mr.pk)
                                    for mr in self.metamorphic_regions]
        )


    def test_contributor_can_create_update_a_sample(self):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.contributor1.auth_token.key
        )

        sample_data = deepcopy(self.sample_data)

        res = client.post('/samples/', sample_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_json = json.loads(res.content.decode('utf-8'))

        updated_sample_number = get_random_str()
        sample_data['number'] = updated_sample_number
        sample_data.update(dict(
            minerals=[
                {
                    "id": str(self.minerals[2].pk),
                    "amount": "y",
                },
                {
                    "id": str(self.minerals[3].pk),
                    "amount": "y",
                },
            ]
        )),

        res = client.put('/samples/{}/'.format(res_json['id']),
                         sample_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_json = json.loads(res.content.decode('utf-8'))

        self.assertEqual(res_json['number'], updated_sample_number)
        self.assertEqual(
            set(mineral['id'] for mineral in res_json['minerals']),
            set(mineral['id'] for mineral in sample_data['minerals'])
        )


    def test_superuser_can_edit_an_unowned_sample(self):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.superuser1.auth_token.key
        )

        sample_data = deepcopy(self.sample_data)

        res = client.post('/samples/', sample_data)
        res_json = json.loads(res.content.decode('utf-8'))

        sample_data['number'] = get_random_str()
        sample_data.update(dict(
            minerals=[
                {
                    "id": str(self.minerals[2].pk),
                    "amount": "y",
                },
                {
                    "id": str(self.minerals[3].pk),
                    "amount": "y",
                },
            ]
        )),

        res = client.put('/samples/{}/'.format(res_json['id']),
                         sample_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_json = json.loads(res.content.decode('utf-8'))

        self.assertEqual(res_json['number'], updated_sample_number)
        self.assertEqual(
            set(mineral['id'] for mineral in res_json['minerals']),
            set(mineral['id'] for mineral in sample_data['minerals'])
        )


    def test_inactive_user_cannot_create_a_sample(self):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.inactive_user.auth_token.key
        )

        res = client.post('/samples/', self.sample_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
