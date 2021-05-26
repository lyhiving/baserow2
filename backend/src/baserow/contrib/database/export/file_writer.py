import abc
import unicodecsv as csv
import time
from typing import Any, Callable

from django.core.paginator import Paginator
from django.db.models import QuerySet

from baserow.contrib.database.api.views.grid.handler import GridViewHandler
from baserow.contrib.database.export.exceptions import ExportJobCanceledException
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import GridView


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
        self.ordered_field_objects = ordered_field_objects

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
    def for_view(cls, view, requesting_user) -> "QuerysetSerializer":
        grid_view = ViewHandler().get_view(view.id, view_model=GridView)
        model = view.table.get_model()
        qs = GridViewHandler().get_rows(
            requesting_user,
            grid_view,
            model,
            search=None,
        )

        ordered_field_objects = []
        ordered_visible_fields = (
            grid_view.get_field_options()
            .filter(hidden=False)
            .order_by("order", "id")
            .values_list("field__id", flat=True)
        )
        for field_id in ordered_visible_fields:
            ordered_field_objects.append(model._field_objects[field_id])
        return cls(qs, ordered_field_objects)
