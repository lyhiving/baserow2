from django.core.files.storage import default_storage
from django.utils.functional import lazy
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.relations import RelatedField

from baserow.api.user_files.serializers import UserFileURLAndThumbnailsSerializerMixin
from baserow.api.user_files.validators import user_file_name_validator
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.core.user_files.handler import UserFileHandler


class FieldSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = ("id", "table_id", "name", "order", "type", "primary")
        extra_kwargs = {
            "id": {"read_only": True},
            "table_id": {"read_only": True},
        }

    @extend_schema_field(OpenApiTypes.STR)
    def get_type(self, instance):
        # It could be that the field related to the instance is already in the context
        # else we can call the specific_class property to find it.
        field = self.context.get("instance_type")

        if not field:
            field = field_type_registry.get_by_model(instance.specific_class)

        return field.type


class SelectOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    value = serializers.CharField(max_length=255, required=True)
    color = serializers.CharField(max_length=255, required=True)


class CreateFieldSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=lazy(field_type_registry.get_types, list)(), required=True
    )

    class Meta:
        model = Field
        fields = ("name", "type")


class UpdateFieldSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=lazy(field_type_registry.get_types, list)(), required=False
    )

    class Meta:
        model = Field
        fields = ("name", "type")
        extra_kwargs = {
            "name": {"required": False},
        }


class StringRelatedSubField(RelatedField):
    """
    A read only field that serializes its target to the string representation of
    a sub field in the target.
    """

    def __init__(self, sub_field_name, **kwargs):
        self.sub_field_name = sub_field_name
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(getattr(value, self.sub_field_name))


class LinkRowValueSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        help_text="The unique identifier of the row in the " "related table."
    )

    def __init__(self, *args, **kwargs):
        value_field_name = kwargs.pop("value_field_name", "value")
        super().__init__(*args, **kwargs)
        self.fields["value"] = serializers.CharField(
            help_text="The primary field's value as a string of the row in the "
            "related table.",
            source=value_field_name,
            required=False,
        )


class LinkRowValueOnlySerializer(serializers.Serializer):
    """
    Same as the LinkRowValueSerializer however only returns the value of the primary
    field in the link table instead of both the value and the id.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("id")


class FileFieldRequestSerializer(serializers.Serializer):
    visible_name = serializers.CharField(
        required=False, help_text="A visually editable name for the field."
    )
    name = serializers.CharField(
        required=True,
        validators=[user_file_name_validator],
        help_text="Accepts the name of the already uploaded user file.",
    )


class FileFieldResponseSerializer(
    UserFileURLAndThumbnailsSerializerMixin, serializers.Serializer
):
    visible_name = serializers.CharField()
    name = serializers.CharField()
    size = serializers.IntegerField()
    mime_type = serializers.CharField()
    is_image = serializers.BooleanField()
    image_width = serializers.IntegerField()
    image_height = serializers.IntegerField()
    uploaded_at = serializers.DateTimeField()

    def get_instance_attr(self, instance, name):
        return instance[name]


class FileNameAndURLResponseSerializer(RelatedField):
    """
    Serializes to the following format for a given file: f"{file.visible_name} ({the
    files storage location url}"
    """

    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        url = self._get_url(value)
        visible_name = value["visible_name"]
        if url is None:
            return visible_name
        else:
            return visible_name + f" ({url})"

    @staticmethod
    def _get_url(instance):
        if "name" in instance:
            path = UserFileHandler().user_file_path(instance["name"])
            url = default_storage.url(path)
            return url
        else:
            return None
