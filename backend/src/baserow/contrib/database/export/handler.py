import uuid
from io import BytesIO

import time
from django.core.files.storage import default_storage
from os.path import join

from django.conf import settings
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
                qs, export_func = exporter.export_view(
                    job.user, job.view, job.export_options, file
                )
            else:
                qs, export_func = exporter.export_table(
                    job.user, job.table, job.export_options, file
                )

            last_percentage_update = time.perf_counter()
            # TODO: How do we pick a chunk size?
            # TODO: Are we ok with the export being inconstant when someone updates
            #  rows during an export run?
            paginator = Paginator(qs.all(), 2000)
            for page in paginator.page_range:
                for row in paginator.page(page).object_list:
                    export_func(row)
                current_time = time.perf_counter()
                # Update every X seconds to match the clients long poll frequency
                if (
                    current_time - last_percentage_update
                    > EXPORT_JOB_UPDATE_FREQUENCY_SECONDS
                    or page == paginator.num_pages
                ):
                    last_percentage_update = time.perf_counter()
                    job.refresh_from_db()
                    if job.is_cancelled():
                        raise ExportJobCanceledException()
                    else:
                        job.progress_percentage = page / paginator.num_pages
                        print(f"Updating percentage to {job.progress_percentage}")
                        job.save()
        return exported_file_name

    def cancel_unfinished_jobs(self, user):
        jobs = ExportJob.unfinished_jobs(user=user)
        jobs.update(status=EXPORT_JOB_CANCELLED_STATUS)

    def finished_export_job(self, export_job, exported_file_name):
        export_job.status = "completed"
        export_job.exported_file_name = exported_file_name
        export_job.expires_at = timezone.now() + timezone.timedelta(hours=1)
        export_job.save()
        return export_job

    def export_file_path(self, exported_file_name):
        return join(settings.EXPORT_FILES_DIRECTORY, exported_file_name)

    def failed_export_job(self, job, e):
        job.status = EXPORT_JOB_FAILED_STATUS
        job.progress_percentage = 0.0
        job.exported_file_name = None
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
