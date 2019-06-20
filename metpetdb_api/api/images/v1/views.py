from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.images.v1.serializers import ImageContainerSerializer, ImageSerializer, ImageTypeSerializer
from apps.images.models import ImageContainer, Image, ImageType
from api.lib.permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly


class ImageContainerViewSet(viewsets.ModelViewSet):
  queryset = ImageContainer.objects.all()
  serializer_class = ImageContainerSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                        IsOwnerOrReadOnly,)

class ImageTypeViewSet(viewsets.ModelViewSet):
  queryset = ImageType.objects.all()
  serializer_class = ImageTypeSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperuserOrReadOnly,)


class ImageViewSet(viewsets.ModelViewSet):
  queryset = Image.objects.all()
  serializer_class = ImageSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

  def get_serializer(self, *args, **kwargs):
    # FIXME not sure what this is doing yet
    # if self.request.method == 'PUT':
      # kwargs['partial'] = True
    return super().get_serializer(*args, **kwargs)

  def perform_create(self, serializer):
    return serializer.save()

  def create(self, request, *args, **kwargs):
    img_file = request.FILES.get('image')
    if not img_file:
      print("no image file")
      return Response(status=404)

    img_data = request.data
    img_data['image'] = img_file


    serializer = self.get_serializer(data=img_data)
    try:
      serializer.is_valid(raise_exception=True)
    except Exception as err:
      return Response(
                data={'error':str(err)},
                status=404)

    instance = self.perform_create(serializer)

    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers)
