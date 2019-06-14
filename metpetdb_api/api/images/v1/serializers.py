import tempfile
from os import sep, listdir
from rest_framework import serializers
from apps.images.models import Image, ImageContainer, ImageType, XrayImage, ImageComments
from apps.samples.models import Sample, Subsample, SubsampleType
from django.core.files import File
import urllib.request
from urllib.parse import urlparse, urlencode, urlunparse
from versatileimagefield.serializers import VersatileImageFieldSerializer
import zipfile
import xlrd
import re
from django.db import transaction
from api.users.v1.serializers import UserSerializer
from apps.users.models import User
from rest_framework.response import Response

SAMPLE_NUMBER = 'samplenumber'
SUBSAMPLE = 'subsample'
SUBSAMPLE_TYPE = 'subsampletype'
PATH = 'path'
FILE = 'file'
IMAGE_TYPE = 'imagetype'
SCALE = 'scale'
COLLECTOR = 'collector'
COMMENT = 'comment'
ELEMENT = 'element'
DWELL_TIME = 'dwelltime'
CURRENT = 'current'
VOLTAGE = 'voltage'
XRAY_IMAGE = 'xraymap'

required_headers = {SAMPLE_NUMBER, IMAGE_TYPE}


class ImageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageType
        fields = ('id', 'image_type', 'abbreviation', 'comments')


class ImageCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageComments
        fields = ('comment_id', 'comment_text', 'version')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'version', 'image_type', 'collector', 'owner', 'public_data', 'scale',
                  'description', 'comments')
    image = VersatileImageFieldSerializer(sizes='image_sizes', required=False)
    image_type = ImageTypeSerializer(read_only=True)
    comments = ImageCommentsSerializer(many=True,required=False)
    owner = UserSerializer(read_only=True)

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if self.initial_data.get('image_type'):
            self._validated_data.update({'image_type':ImageType.objects.get(pk=self.initial_data['image_type'])})
        
        if self.initial_data.get('owner'):
            self._validated_data.update(
                {'owner': User.objects.get(pk=self.initial_data['owner'])})

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in self.fields:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance


class ImageContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageContainer
        fields = ('id', 'description', 'url', 'images')

    images = ImageSerializer(many=True, read_only=True)

    @staticmethod
    def get_worksheet_row_values(worksheet, row_number):
        return [x.value for x in worksheet.row(row_number)]

    @staticmethod
    def extract_zip_file_from_url(url, destination):
        with tempfile.TemporaryFile() as zip_tmp:
            with urllib.request.urlopen(url) as image_zip:
                zip_tmp.write(image_zip.read())

            with zipfile.ZipFile(zip_tmp, 'r') as zip_ref:
                zip_ref.extractall(destination)

    @staticmethod
    def get_xls_file_name(directory):
        xls_file_names = [file_name for file_name in listdir(directory) if file_name.endswith('.xls')]
        if len(xls_file_names) != 1:
            return Response(
                data={'error': 'Expected exactly 1 .xls file, but {} files were provided'.format(len(xls_file_names))},
                status=400
            )

        return xls_file_names[0]

    @staticmethod
    def get_worksheet_header_mappings(directory, xls_file):
        workbook = xlrd.open_workbook('{}{}{}'.format(directory, sep, xls_file))
        worksheet = workbook.sheet_by_index(0)
        header_row = [x.value.replace(' ', '').lower() for x in worksheet.row(0)]

        if not set(header_row) >= required_headers:
            raise serializers.ValidationError('Missing required headers {}'.format(required_headers-set(header_row)))
        if PATH not in header_row and FILE not in header_row:
            raise serializers.ValidationError('Missing required header path/file')

        header_to_index = {COMMENT: set()}
        for index, header in enumerate(header_row):
            if header == COMMENT:
                header_to_index[COMMENT].add(index)
            else:
                header_to_index[header] = index
        return worksheet, header_to_index

    @staticmethod
    def parse_dropbox_url(url):
        # first add the ?dl=1 to the url if not present or if 0
        parsed_url = list(urlparse(url))
        drop_box_params = {'dl': '1'}
        parsed_url[4] = urlencode(drop_box_params)
        return urlunparse(parsed_url)

    def create_image(self, base_directory, path, image_container, image_type, collector, scale,
                     sample, subsample, public_data):
        with open(sep.join((base_directory, path)), 'rb') as file_contents:
            try:
                image_type_obj = ImageType.objects.get(image_type__iexact=image_type)
            except ImageType.DoesNotExist:
                image_type_obj = None
            if not image_type_obj:
                image_type_obj = ImageType.objects.get(abbreviation__iexact=image_type)

            owner = None
            if self.initial_data.get('owner'):
                owner = User.objects.get(pk=self.initial_data['owner'])

            new_image = Image.objects.create(image_container=image_container,
                                             image_type=image_type_obj,
                                             collector=collector,
                                             scale=scale,
                                             sample=sample,
                                             subsample=subsample,
                                             public_data=public_data,
                                             owner=owner)

            file_name = path[path.rfind(sep) + 1:]
            new_image.image.save(file_name, File(file_contents))
            new_image.save()
            return new_image

    def get_sample_subsample_public_data(self, subsample_name, sample_number, subsample_type):
        sample, subsample, public_data = None, None, False
        if self.initial_data.get('owner'):
                owner = User.objects.get(pk=self.initial_data['owner'])
        if not subsample_name or len(subsample_name) == 0:
            sample = Sample.objects.get(number=sample_number,owner=owner)
            public_data = sample.public_data
        else:
            subsample_sample = Sample.objects.get(number=sample_number,owner=owner)
            try:
                subsample = Subsample.objects.get(sample=subsample_sample, name=subsample_name)
            except Subsample.DoesNotExist:
                owner = None
                if self.initial_data.get('owner'):
                    owner = User.objects.get(pk=self.initial_data['owner'])
                subsample = Subsample.objects.create(
                    name=subsample_name,
                    sample=subsample_sample,
                    subsample_type=SubsampleType.objects.get(name=subsample_type),
                    owner=owner
                )
            public_data = subsample.public_data
        return sample, subsample, public_data

    @staticmethod
    def create_xray_image(image_type, values, header_to_index, created_image, dwell_time, current, voltage):
        image_type_value = re.sub('[^a-z]+', '', image_type.lower())
        print(image_type_value)
        if image_type_value == XRAY_IMAGE:
            element = values[header_to_index[ELEMENT]]
            if not element:
                raise serializers.ValidationError('Expected element for xray image, but none provided')
            xray_image = XrayImage.objects.create(image=created_image,
                                                  dwelltime=dwell_time,
                                                  current=current,
                                                  voltage=voltage,
                                                  element=element)
            xray_image.save()

    @staticmethod
    def create_image_comments(image, comments):
        ImageComments.objects.bulk_create([ImageComments(
            image=image,
            comment_text=comment
        ) for comment in comments])

    def process_worksheet(self, worksheet, header_to_index, base_directory, image_container):
        num_rows = worksheet.nrows

        for i in range(1, num_rows):
            values = ImageContainerSerializer.get_worksheet_row_values(worksheet, i)
            sample_number = values[header_to_index[SAMPLE_NUMBER]]  # required
            subsample_name = values[header_to_index[SUBSAMPLE]] if SUBSAMPLE in header_to_index else None
            subsample_type = values[header_to_index[SUBSAMPLE_TYPE]] if SUBSAMPLE_TYPE in header_to_index else None
            path_to_replace = values[header_to_index[PATH]] if PATH in header_to_index else values[header_to_index[FILE]]
            path = re.sub(r'[\\/]', sep, path_to_replace)
            image_type = values[header_to_index[IMAGE_TYPE]]  # required
            scale = values[header_to_index[SCALE]] if SCALE in header_to_index else None
            collector = values[header_to_index[COLLECTOR]] if COLLECTOR in header_to_index else None
            comments = {values[comment_index] for comment_index in header_to_index[COMMENT] if len(values[comment_index].strip()) > 0} if COMMENT in header_to_index else None
            dwell_time = values[header_to_index[DWELL_TIME]] if DWELL_TIME in header_to_index else None
            current = values[header_to_index[CURRENT]] if CURRENT in header_to_index else None
            voltage = values[header_to_index[VOLTAGE]] if VOLTAGE in header_to_index else None

            if not scale:
                scale = None

            sample, subsample, public_data = self.get_sample_subsample_public_data(subsample_name,
                                                                                   sample_number, subsample_type)

            created_image = self.create_image(base_directory, path, image_container, image_type,
                                              collector, scale, sample, subsample, public_data)

            if image_type:
                ImageContainerSerializer.create_xray_image(image_type, values, header_to_index, created_image,
                                                           dwell_time, current, voltage)

            if comments:
                ImageContainerSerializer.create_image_comments(created_image, comments)

    @transaction.atomic
    def create(self, validated_data):
        new_image_container = ImageContainer.objects.create(**validated_data)
        url = self.parse_dropbox_url(validated_data['url'])

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.extract_zip_file_from_url(url, tmp_dir)
            xls_file = self.get_xls_file_name(tmp_dir)
            worksheet, header_to_index = self.get_worksheet_header_mappings(tmp_dir, xls_file)
            self.process_worksheet(worksheet, header_to_index, tmp_dir, new_image_container)

        return new_image_container
