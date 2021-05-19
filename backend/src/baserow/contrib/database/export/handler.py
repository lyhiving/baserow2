import logging
import time
import uuid
from io import BytesIO
from os.path import join
from typing import Optional, Dict, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from baserow.contrib.database.export.models import (
    ExportJob,
    EXPORT_JOB_EXPORTING_STATUS,
    EXPORT_JOB_CANCELLED_STATUS,
    EXPORT_JOB_PENDING_STATUS,
    EXPORT_JOB_FAILED_STATUS,
    EXPORT_JOB_EXPIRED_STATUS,
    EXPORT_JOB_COMPLETED_STATUS,
)
from .exceptions import (
    ExportJobCanceledException,
    TableOnlyExportUnsupported,
    ViewUnsupportedForExporterType,
)
from .registries import table_exporter_registry
from ..table.models import Table
from ..views.models import View
from ..views.registries import view_type_registry

logger = logging.getLogger(__name__)

# Ensure this matches the clients export job long poll frequency
EXPORT_JOB_UPDATE_FREQUENCY_SECONDS = 1

User = get_user_model()


class ExportHandler:
    @staticmethod
    def create_pending_export_job(
        user: User, table: Table, view: Optional[View], export_options: Dict[str, Any]
    ):
        """
        Creates a new pending export job configured with the providing options but does
        not start the job. Will cancel any previously running jobs for this user.

        :param user: The user who the export job is being run for.
        :param table: The table on which the job is being run.
        :param view: An optional view of the table to export instead of the table
            itself.
        :param export_options: A dict containing exporter_type and the relevant options
            for that type.
        :return:
        """

        _cancel_unfinished_jobs(user)

        exporter_type = export_options.pop("exporter_type")

        exporter = table_exporter_registry.get(exporter_type)
        if not exporter.can_export_table and view is None:
            raise TableOnlyExportUnsupported()

        if view is not None:
            view_type = view_type_registry.get_by_model(view.specific_class)
            if view_type.type not in exporter.supported_views:
                raise ViewUnsupportedForExporterType()

        job = ExportJob.objects.create(
            user=user,
            table=table,
            view=view,
            exporter_type=exporter_type,
            status=EXPORT_JOB_PENDING_STATUS,
            expires_at=timezone.now()
            + timezone.timedelta(minutes=settings.EXPORT_FILE_DURATION_MINUTES),
            export_options=export_options,
        )
        return job

    @staticmethod
    def run_export_job(job):
        """
        Given an export job will run the export and store the result in the configured
        storage.

        :param job: The job to run.
        :return: An updated ExportJob instance with the exported file name.
        """

        try:
            exported_file_name = _run_export_job(job)
        except Exception as e:
            _failed_export_job(job, e)
            raise e

        return _finished_export_job(job, exported_file_name)

    @staticmethod
    def export_file_path(exported_file_name):
        """
        Given an export file name returns the path to where that export file should be
        put in storage.
        :param exported_file_name: The name of the file to generate a path for.
        :return: The path where this export file should be put in storage.
        """

        return join(settings.EXPORT_FILES_DIRECTORY, exported_file_name)

    @staticmethod
    def clean_up_old_jobs():
        """
        Cleans up expired export jobs, will delete any files in storage for expired
        jobs with exported files, will cancel any exporting or pending jobs which have
        also expired.
        """
        jobs = ExportJob.jobs_requiring_cleanup(timezone.now())
        logger.info(f"Cleaning up {jobs.count()} old jobs")
        for job in jobs:
            with transaction.atomic():
                if job.exported_file_name:
                    default_storage.delete(
                        ExportHandler.export_file_path(job.exported_file_name)
                    )
                    job.exported_file_name = None

                job.status = EXPORT_JOB_EXPIRED_STATUS
                job.save()


def _cancel_unfinished_jobs(user):
    """
    Will cancel any in progress jobs by setting their status to cancelled. Any
    tasks currently running these jobs are expected to periodically check if they
    have been cancelled and stop accordingly.

    :param user: The user to cancel all unfinished jobs for.
    :return The number of jobs cancelled.
    """

    jobs = ExportJob.unfinished_jobs(user=user)
    return jobs.update(status=EXPORT_JOB_CANCELLED_STATUS)


def _finished_export_job(export_job, exported_file_name):
    """
    Marks the provided job as finished with the result being the provided file name.
    :param export_job: The job to update to be finished.
    :param exported_file_name: The file name to set on the job.
    :return: The updated finished job.
    """

    export_job.status = EXPORT_JOB_COMPLETED_STATUS
    export_job.exported_file_name = exported_file_name
    export_job.expires_at = timezone.now() + timezone.timedelta(hours=1)
    export_job.save()
    return export_job


def _failed_export_job(job, e):
    """
    Marks the given export job as failed and stores the exception in the job.
    :param job: The job to mark as failed
    :param e: The exception causing the failure
    :return: The updated failed job.
    """

    job.status = EXPORT_JOB_FAILED_STATUS
    job.progress_percentage = 0.0
    job.error = str(e)
    job.expires_at = timezone.now()
    job.save()
    return job


def _check_and_update_job(job, last_update_time, current_row, total_rows):
    """
    Given a job and a time.perf_counter param which should be the last time this
    function was called will update the progress percentage of the job if enough time
    has elapsed. Will also raise a ExportJobCanceledException exception if the job
    has been cancelled, but will only check this if enough time has elapsed since the
    last check.
    :param job: The job to check and update progress for.
    :param last_update_time: a time.perf_counter value of the last time this function
        was called.
    :param current_row: An int indicating the current row this export job has
        exported upto
    :param total_rows: An int of the total number of rows this job is exporting.
    :return: An updated time.perf_counter indicating the last time the check was run
    """

    current_time = time.perf_counter()
    # We check only every so often as we don't need per row granular updates as the
    # client is only polling every X seconds also.
    enough_time_has_passed = (
        current_time - last_update_time > EXPORT_JOB_UPDATE_FREQUENCY_SECONDS
    )
    is_last_row = current_row == total_rows
    if enough_time_has_passed or is_last_row:
        last_update_time = time.perf_counter()
        job.refresh_from_db()
        if job.is_cancelled_or_expired():
            raise ExportJobCanceledException()
        else:
            job.progress_percentage = current_row / total_rows
            job.save()
    return last_update_time


def _export_all_rows(job, qs, export_row_func):
    """
    Iterates through the given queryset using a paginator to ensure constant memory
    usage. Calls export_row_fun on every item returned from the queryset. Will update
    the provided job as we progress through the iteration with the current progress.

    Raises ExportJobCanceledException if the job is cancelled during the iteration
    and export of the queryset.

    :param job:
    :param qs:
    :param export_row_func:
    """

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


def _create_storage_dir_if_missing_and_open(storage_location):
    """
    Attempts to open the provided storage location in binary overwriting write mode.
    If it encounters a FileNotFound error will attempt to create the folder structure
    leading upto to the storage location and then open again.

    :param storage_location: The storage location to open and ensure folders for.
    :return: The open file descriptor for the storage_location
    """

    try:
        return default_storage.open(storage_location, "wb+")
    except FileNotFoundError:
        # django's file system storage will not attempt to creating a missing
        # EXPORT_FILES_DIRECTORY and instead will throw a FileNotFoundError.
        # So we first save an empty file which will create any missing directories
        # and then open again.
        default_storage.save(storage_location, BytesIO())
        return default_storage.open(storage_location, "wb")


def _run_export_job(job):
    """
    Using the jobs exporter type exports all data into a new file placed in the
    default storage.

    :rtype: The filename of the resulting export stored in the default storage.
    """

    job.status = EXPORT_JOB_EXPORTING_STATUS
    job.save()
    exporter = table_exporter_registry.get(job.exporter_type)

    exported_file_name = str(uuid.uuid4()) + exporter.file_extension
    storage_location = ExportHandler.export_file_path(exported_file_name)

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
