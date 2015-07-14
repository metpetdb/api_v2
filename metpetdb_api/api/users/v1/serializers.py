from django.contrib.auth import get_user_model

from api.lib.serializers import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name', 'address', 'city', 'province',
                  'country', 'postal_code', 'is_active', 'is_contributor',
                  'professional_url', 'is_superuser')
