import pytest

from baserow.api.exceptions import RequestBodyValidationException
from baserow.api.utils import validate_data
from baserow.contrib.database.api.export.serializers import CreateExportJobSerializer


@pytest.mark.django_db
def test_polymorphic_export_options_serializer_allows_correct_data(data_fixture):
    initial_data = {
        "exporter_type": "csv",
        "csv_encoding": "utf-8",
        "csv_column_separator": "comma",
        "csv_include_header": False,
    }
    data = validate_data(
        CreateExportJobSerializer,
        initial_data,
    )

    assert data == {
        "exporter_type": "csv",
        "csv_encoding": "utf-8",
        "csv_column_separator": ",",
        "csv_include_header": False,
    }


@pytest.mark.django_db
def test_polymorphic_export_options_serializer_fails_on_missing_exporter_type(
    data_fixture,
):
    initial_data = {
        "csv_encoding": "utf-8",
        "csv_column_separator": "comma",
        "csv_include_header": False,
    }
    with pytest.raises(RequestBodyValidationException):
        validate_data(
            CreateExportJobSerializer,
            initial_data,
        )


@pytest.mark.django_db
def test_polymorphic_export_options_serializer_fails_on_unknown_exporter_type(
    data_fixture,
):
    initial_data = {
        "exporter_type": "csvv",
        "csv_encoding": "utf-8",
        "csv_column_separator": "comma",
        "csv_include_header": False,
    }
    with pytest.raises(RequestBodyValidationException):
        validate_data(
            CreateExportJobSerializer,
            initial_data,
        )
