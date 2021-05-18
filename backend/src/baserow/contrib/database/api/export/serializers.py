from django.core.files.storage import default_storage
from django.utils.functional import lazy
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, fields

from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.export.models import ExportJob

# Please keep in sync with
# web-frontend/modules/core/components/helpers/CharsetDropdown.vue:
from baserow.contrib.database.export.registries import table_exporter_registry

SUPPORTED_CSV_CHARSETS = [
    ("utf-8", "Unicode (UTF-8)"),
    ("iso-8859-6", "Arabic (ISO-8859-6)"),
    ("windows-1256", "Arabic (Windows-1256)"),
    ("iso-8859-4", "Baltic (ISO-8859-4)"),
    ("windows-1257", "Baltic (windows-1257)"),
    ("iso-8859-14", "Celtic (ISO-8859-14)"),
    ("iso-8859-2", "Central European (ISO-8859-2)"),
    ("windows-1250", "Central European (Windows-1250)"),
    ("gbk", "Chinese, Simplified (GBK)"),
    ("gb18030", "Chinese (GB18030)"),
    ("big5", "Chinese Traditional (Big5)"),
    ("koi8-r", "Cyrillic (KOI8-R)"),
    ("koi8-u", "Cyrillic (KOI8-U)"),
    ("iso-8859-5", "Cyrillic (ISO-8859-5)"),
    ("windows-1251", "Cyrillic (Windows-1251)"),
    ("x-mac-cyrillic", "Cyrillic Mac OS (x-mac-cyrillic)"),
    ("iso-8859-7", "Greek (ISO-8859-7)"),
    ("windows-1253", "Greek (Windows-1253)"),
    ("iso-8859-8", "Hebrew (ISO-8859-8)"),
    ("windows-1255", "Hebrew (Windows-1255)"),
    ("euc-jp", "Japanese (EUC-JP)"),
    ("iso-2022-jp", "Japanese (ISO-2022-JP)"),
    ("shift-jis", "Japanese (Shift-JIS)"),
    ("euc-kr", "Korean (EUC-KR)"),
    ("macintosh", "Macintosh"),
    ("iso-8859-10", "Nordic (ISO-8859-10)"),
    ("iso-8859-16", "South-Eastern European (ISO-8859-16)"),
    ("windows-874", "Thai (Windows-874)"),
    ("windows-1254", "Turkish (Windows-1254)"),
    ("windows-1258", "Vietnamese (Windows-1258)"),
    ("iso-8859-1", "Western European (ISO-8859-1)"),
    ("windows-1252", "Western European (Windows-1252)"),
    ("iso-8859-3", "Latin 3 (ISO-8859-3)"),
]
SUPPORTED_CSV_COLUMN_SEPARATORS = [
    ("comma", ","),
    ("semi", ";"),
    ("pipe", "|"),
    ("tab", "\t"),
    ("record_separator", "\x1e"),
    ("unit_separator", "\x1f"),
]


class ExportedFileURLSerializerMixin(serializers.Serializer):
    url = serializers.SerializerMethodField()

    def get_instance_attr(self, instance, name):
        return getattr(instance, name)

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, instance):
        name = self.get_instance_attr(instance, "exported_file_name")
        if name:
            path = ExportHandler().export_file_path(name)
            url = default_storage.url(path)
            return url
        else:
            return None


class GetExportJobSerializer(
    ExportedFileURLSerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = ExportJob
        fields = [
            "id",
            "table",
            "view",
            "exporter_type",
            "status",
            "exported_file_name",
            "error",
            "expires_at",
            "progress_percentage",
            "url",
        ]


class DisplayChoiceField(serializers.ChoiceField):
    """
    Just like a choice field but returns the second value of each choice tuple when
    serialized.
    """

    def to_representation(self, obj):
        return self._choices[obj]


class ExporterTypeSerializer(serializers.Serializer):
    exporter_type = fields.ChoiceField(
        choices=lazy(table_exporter_registry.get_types, list)()
    )


class RequestCsvOptionSerializer(ExporterTypeSerializer):
    csv_charset = fields.ChoiceField(choices=SUPPORTED_CSV_CHARSETS)
    # For ease of use we expect the JSON to contain human typeable forms of each
    # different separator instead of the unicode character itself. By using the
    # DisplayChoiceField we can then map this to the actual separator character by
    # having those be the second value of each choice tuple.
    csv_column_separator = DisplayChoiceField(choices=SUPPORTED_CSV_COLUMN_SEPARATORS)
    csv_include_header = fields.BooleanField()
