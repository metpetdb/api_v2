from django.http.request import QueryDict
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if self.context.get('request'):
            if isinstance(self.context['request'].data, QueryDict):
                self.context['request'].data._mutable = True

            if self.context['request'].method == 'POST':
                # An object's owner should be the user making the request;
                # objects which don't have an owner can just ignore this
                self.context['request'].data['owner'] = str(
                    self.context['request'].user.pk
                )
            elif self.context['request'].method == 'PUT':
                # Don't allow PUT operations to update an object's owner
                self.context['request'].data.pop('owner', None)

            if isinstance(self.context['request'].data, QueryDict):
                self.context['request'].data._mutable = False
        try:
            fields = self.context['request'].query_params.get('fields')
        except KeyError:
            fields = None

        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
