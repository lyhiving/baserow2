import time
from typing import BinaryIO

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from baserow.contrib.database.api.views.grid.handler import GridViewHandler
from baserow.contrib.database.export.exceptions import ExportJobCanceledException
from baserow.contrib.database.export.models import (
    ExportJob,
)
from baserow.contrib.database.export.registries import (
    TableExporter,
)
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import View, GridView

User = get_user_model()


# Ensure this matches the clients export job long poll frequency
EXPORT_JOB_UPDATE_FREQUENCY_SECONDS = 1


def run_export_job_to_file(
    job: ExportJob,
    exporter: TableExporter,
    export_file: BinaryIO,
):
    """
    Runs an export job and stores the result in the provided export file.
    """
    if job.view is None:
        # The job is not for a specific view, export just the table as it is.
        queryset, ordered_field_objects = _get_table_queryset_and_fields(job.table)
    else:
        (
            queryset,
            ordered_field_objects,
        ) = _get_sorted_filtered_ordered_for_view_queryset_and_fields(
            job.user, job.view
        )

    export_row_func = exporter.get_row_export_function(
        ordered_field_objects, job.export_options, export_file
    )
    _run_export(job, queryset, export_row_func)


def _get_sorted_filtered_ordered_for_view_queryset_and_fields(
    requesting_user: User, view: View
):
    """
    Constructs the queryset and fields to correctly export this view. Will use the views
    filters, sorts, field orders, hidden fields etc to return a queryset which exactly
    matches what the user sees when they visit the view in baserow.

    :param requesting_user: The user who is requesting the export job.
    :param view: The view to export.
    :return: A tuple of the sorted and filtered queryset with an ordered list of
       fields which are visible in this view.
    """
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
    return qs, ordered_field_objects


def _get_table_queryset_and_fields(table: Table):
    model = table.get_model()
    qs = model.objects.all().enhance_by_fields()
    ordered_field_objects = model._field_objects.values()
    return qs, ordered_field_objects


def _run_export(job, qs, export_row_func):
    """
    Iterates through the given queryset using a paginator to ensure constant memory
    usage. Calls export_row_func on every item returned from the queryset. Will update
    the provided job as we progress through the iteration with the current progress.

    Raises ExportJobCanceledException if the job is cancelled during the iteration
    and export of the queryset.

    :param job:
    :param qs:
    :param export_row_func:
    """

    last_check = time.perf_counter()
    paginator = Paginator(qs.all(), 2000)
    i = 0
    for page in paginator.page_range:
        for row in paginator.page(page).object_list:
            i = i + 1
            export_row_func(row)
            last_check = _check_and_update_job(job, last_check, i, paginator.count)


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
