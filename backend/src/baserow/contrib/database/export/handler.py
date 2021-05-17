import time
import uuid
from io import BytesIO
from os.path import join

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.utils import timezone

from baserow.contrib.database.export.models import (
    ExportJob,
    EXPORT_JOB_EXPORTING_STATUS,
    EXPORT_JOB_CANCELLED_STATUS,
    EXPORT_JOB_PENDING_STATUS,
    EXPORT_JOB_FAILED_STATUS,
)
from .exceptions import ExportJobCanceledException
from .registries import table_exporter_registry

# Ensure this matches the clients export job long poll frequency
EXPORT_JOB_UPDATE_FREQUENCY_SECONDS = 1


def _check_and_update_job(job, last_update_time, current_row, total_rows):
    current_time = time.perf_counter()
    # Update every X seconds to match the clients long poll frequency
    enough_time_has_passed = (
        current_time - last_update_time > EXPORT_JOB_UPDATE_FREQUENCY_SECONDS
    )
    is_last_row = current_row == total_rows
    if enough_time_has_passed or is_last_row:
        last_update_time = time.perf_counter()
        job.refresh_from_db()
        if job.is_cancelled():
            raise ExportJobCanceledException()
        else:
            job.progress_percentage = current_row / total_rows
            job.save()
    return last_update_time


def _export_all_rows(job, qs, export_row_func):
    last_check = time.perf_counter()
    # TODO: How do we pick a chunk size?
    # TODO: Are we ok with the export being inconstant when someone updates
    #  rows during an export run?
    paginator = Paginator(qs.all(), 2000)
    i = 0
    for page in paginator.page_range:
        for row in paginator.page(page).object_list:
            i = i + 1
            export_row_func(row)
            last_check = _check_and_update_job(job, last_check, i, paginator.count)


class ExportHandler:
    def create_pending_export_job(
        self, user, table, view, exporter_type, export_options
    ):
        self.cancel_unfinished_jobs(user)

        job = ExportJob.objects.create(
            user=user,
            table=table,
            view=view,
            exporter_type=exporter_type,
            status=EXPORT_JOB_PENDING_STATUS,
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            export_options=export_options,
        )
        return job

    def run_export_job(self, job):
        try:
            exported_file_name = self._run_export_job(job)
        except Exception as e:
            self.failed_export_job(job, e)
            raise e

        return self.finished_export_job(job, exported_file_name)

    def _run_export_job(self, job):
        job.status = EXPORT_JOB_EXPORTING_STATUS
        job.save()
        exporter = table_exporter_registry.get(job.exporter_type)

        exported_file_name = str(uuid.uuid4()) + exporter.file_extension
        storage_location = self.export_file_path(exported_file_name)

        with _create_storage_dir_if_missing_and_open(storage_location) as file:
            if job.view:
                qs, export_row_func = exporter.export_view(
                    job.user, job.view, job.export_options, file
                )
            else:
                qs, export_row_func = exporter.export_table(
                    job.user, job.table, job.export_options, file
                )

            _export_all_rows(job, qs, export_row_func)

        return exported_file_name

    @staticmethod
    def cancel_unfinished_jobs(user):
        jobs = ExportJob.unfinished_jobs(user=user)
        jobs.update(status=EXPORT_JOB_CANCELLED_STATUS)

    @staticmethod
    def finished_export_job(export_job, exported_file_name):
        export_job.status = "completed"
        export_job.exported_file_name = exported_file_name
        export_job.expires_at = timezone.now() + timezone.timedelta(hours=1)
        export_job.save()
        return export_job

    @staticmethod
    def export_file_path(exported_file_name):
        return join(settings.EXPORT_FILES_DIRECTORY, exported_file_name)

    @staticmethod
    def failed_export_job(job, e):
        job.status = EXPORT_JOB_FAILED_STATUS
        job.progress_percentage = 0.0
        job.exported_file_name = None
        job.error = str(e)
        job.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        job.save()
        return job


def _create_storage_dir_if_missing_and_open(storage_location):
    try:
        return default_storage.open(storage_location, "wb+")
    except FileNotFoundError:
        # django's file system storage will not attempt to creating a missing
        # EXPORT_FILES_DIRECTORY and instead will throw a FileNotFoundError.
        # So we first save an empty file which will create any missing directories
        # and then open again.
        default_storage.save(storage_location, BytesIO())
        return default_storage.open(storage_location, "wb")
