from rest_framework import viewsets
from api.images.v1.serializers import ImageContainerSerializer, ImageSerializer
from apps.images.models import ImageContainer, Image
from rest_framework import permissions, status, viewsets
from api.lib.permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly


class ImageContainerViewSet(viewsets.ModelViewSet):
    queryset = ImageContainer.objects.all()
    serializer_class = ImageContainerSerializer
    # FIXME
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,
    #                       IsOwnerOrReadOnly,)

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # TODO add permissions
