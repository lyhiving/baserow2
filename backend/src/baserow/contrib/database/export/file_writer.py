import abc
import time
from typing import Any, Callable

import unicodecsv as csv
from django.core.paginator import Paginator
from django.db.models import QuerySet

from baserow.contrib.database.export.exceptions import ExportJobCanceledException
from baserow.contrib.database.table.models import FieldObject
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.registries import view_type_registry


class FileWriter(abc.ABC):
    def __init__(self, file):
        self._file = file

    @abc.abstractmethod
    def write_bytes(self, value: bytes):
        pass

    @abc.abstractmethod
    def write(self, value: str, encoding="utf-8"):
        pass

    @abc.abstractmethod
    def write_rows(
        self,
        queryset: QuerySet,
        write_row: Callable[[Any, bool], None],
    ):
        pass

    def get_csv_dict_writer(self, headers, **kwargs):
        return csv.DictWriter(self._file, headers, **kwargs)


class PaginatedExportJobFileWriter(FileWriter):
    EXPORT_JOB_UPDATE_FREQUENCY_SECONDS = 1

    def __init__(self, file, job):
        super().__init__(file)
        self.job = job
        self.last_check = None

    def write_bytes(self, value: bytes):
        self._file.write(value)

    def write(self, value: str, encoding="utf-8"):
        self._file.write(value.encode(encoding))

    def write_rows(self, queryset, write_row):
        self.last_check = time.perf_counter()
        paginator = Paginator(queryset.all(), 2000)
        i = 0
        for page in paginator.page_range:
            for row in paginator.page(page).object_list:
                i = i + 1
                is_last_row = i == paginator.count
                write_row(row, is_last_row)
                self._check_and_update_job(i, paginator.count)

    def _check_and_update_job(self, current_row, total_rows):
        """
        Checks if enough time has passed and if so checks the status of the job and
        updates its progress percentage.
        Will raise a ExportJobCanceledException exception if when a check occurs
        the job has been cancelled.
        :param current_row: An int indicating the current row this export job has
            exported upto
        :param total_rows: An int of the total number of rows this job is exporting.
        """

        current_time = time.perf_counter()
        # We check only every so often as we don't need per row granular updates as the
        # client is only polling every X seconds also.
        enough_time_has_passed = (
            current_time - self.last_check > self.EXPORT_JOB_UPDATE_FREQUENCY_SECONDS
        )
        is_last_row = current_row == total_rows
        if enough_time_has_passed or is_last_row:
            self.last_check = time.perf_counter()
            self.job.refresh_from_db()
            if self.job.is_cancelled_or_expired():
                raise ExportJobCanceledException()
            else:
                self.job.progress_percentage = current_row / total_rows
                self.job.save()


class QuerysetSerializer(abc.ABC):
    def __init__(self, queryset, ordered_field_objects):
        self.queryset = queryset
        self.field_serializers = [lambda row: ("id", "id", row.id)]

        for field_object in ordered_field_objects:
            self.field_serializers.append(self._get_field_serializer(field_object))

    @abc.abstractmethod
    def write_to_file(self, file_writer: FileWriter, **kwargs):
        pass

    @classmethod
    def for_table(cls, table) -> "QuerysetSerializer":
        model = table.get_model()
        qs = model.objects.all().enhance_by_fields()
        ordered_field_objects = model._field_objects.values()
        return cls(qs, ordered_field_objects)

    @classmethod
    def for_view(cls, view) -> "QuerysetSerializer":
        view_type = view_type_registry.get_by_model(view.specific_class)
        fields, model = view_type.get_fields_and_model(view)
        qs = ViewHandler().get_queryset(view, model=model)
        return cls(qs, fields)

    @staticmethod
    def _get_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
        def serializer_func(row):
            attr = getattr(row, field_object["name"])

            if attr is None:
                result = ""
            else:
                result = field_object["type"].get_human_export_value(row, field_object)

            return (
                field_object["name"],
                field_object["field"].name,
                result,
            )

        return serializer_func
