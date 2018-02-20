import tempfile
from os import walk, sep
from rest_framework import serializers
from apps.images.models import Image, ImageContainer
from django.core.files import File
import urllib.request
from versatileimagefield.serializers import VersatileImageFieldSerializer
import zipfile


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image')
    image = VersatileImageFieldSerializer(sizes='image_sizes', required=False)


class ImageContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageContainer
        fields = ('id', 'description', 'url', 'images')

    images = ImageSerializer(many=True, read_only=True)

    def create(self, validated_data):
        new_image_container = ImageContainer.objects.create(**validated_data)
        url = validated_data['url']  # zip file url

        with tempfile.TemporaryDirectory() as tmp_dir:
            with tempfile.TemporaryFile() as zip_tmp:
                with urllib.request.urlopen(url) as image_zip:
                    zip_tmp.write(image_zip.read())

                with zipfile.ZipFile(zip_tmp, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)

            for (dir_path, dir_names, file_names) in walk(tmp_dir):
                for file_name in file_names:
                    print(sep.join((dir_path, file_name)))
                    with open(sep.join((dir_path, file_name)), 'rb') as file_contents:
                        new_image = Image.objects.create(image_container=new_image_container)
                        new_image.image.save(file_name, File(file_contents))
                        new_image.save()

        return new_image_container
