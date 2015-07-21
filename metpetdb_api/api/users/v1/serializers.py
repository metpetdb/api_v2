from django.contrib.auth import get_user_model

from api.lib.serializers import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name',)
