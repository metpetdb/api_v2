from django.contrib.auth import get_user_model

from api.lib.serializers import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'email', 'address' , 'city', 'province',
                  'country', 'postal_code', 'institution',
                  'professional_url', 'research_interests')
