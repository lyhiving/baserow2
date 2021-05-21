from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q

from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View

User = get_user_model()

EXPORT_JOB_EXPORTING_STATUS = "exporting"
EXPORT_JOB_FAILED_STATUS = "failed"
EXPORT_JOB_CANCELLED_STATUS = "cancelled"
EXPORT_JOB_PENDING_STATUS = "pending"
EXPORT_JOB_EXPIRED_STATUS = "expired"
EXPORT_JOB_COMPLETED_STATUS = "complete"
EXPORT_JOB_STATUS_CHOICES = [
    (EXPORT_JOB_PENDING_STATUS, EXPORT_JOB_PENDING_STATUS),
    (EXPORT_JOB_EXPORTING_STATUS, EXPORT_JOB_EXPORTING_STATUS),
    (EXPORT_JOB_CANCELLED_STATUS, EXPORT_JOB_CANCELLED_STATUS),
    (EXPORT_JOB_COMPLETED_STATUS, EXPORT_JOB_COMPLETED_STATUS),
    (EXPORT_JOB_FAILED_STATUS, EXPORT_JOB_FAILED_STATUS),
    (EXPORT_JOB_EXPIRED_STATUS, EXPORT_JOB_EXPIRED_STATUS),
]
EXPORT_JOB_RUNNING_STATUSES = [EXPORT_JOB_PENDING_STATUS, EXPORT_JOB_EXPORTING_STATUS]


class ExportJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    # An export job might be for just a table and not a particular view of that table
    # , in that situation the view will be None.
    view = models.ForeignKey(View, on_delete=models.CASCADE, null=True, blank=True)
    # New exporter types might be registered dynamically by plugins hence we can't
    # restrict this field to a particular choice of options as we don't know them.
    exporter_type = models.TextField()
    status = models.TextField(choices=EXPORT_JOB_STATUS_CHOICES)
    exported_file_name = models.TextField(
        null=True,
        blank=True,
    )
    error = models.TextField(null=True, blank=True)
    # After this time the exported file is no longer guaranteed to exist and will be
    # deleted by a clean up job.
    expires_at = models.DateTimeField()
    # A float going from 0.0 to 1.0 indicating how much progress has been made on the
    # export.
    progress_percentage = models.FloatField(default=0.0)
    export_options = JSONField()

    def is_cancelled_or_expired(self):
        return self.status in [EXPORT_JOB_CANCELLED_STATUS, EXPORT_JOB_EXPIRED_STATUS]

    @staticmethod
    def unfinished_jobs(user):
        return ExportJob.objects.filter(user=user).filter(
            status__in=EXPORT_JOB_RUNNING_STATUSES
        )

    @staticmethod
    def jobs_requiring_cleanup(current_time):
        """
        Returns jobs which have passed their expires_at time and require cleanup. A job
        requires cleanup if it either has an exported_file_name and hence we want to
        delete that file OR if the job is still has a running status.

        :param current_time: Any export job with an expires_at less than this time is
            considered expired.
        :return: A queryset of export jobs that require clean up.
        """

        return ExportJob.objects.filter(expires_at__lte=current_time).filter(
            Q(exported_file_name__isnull=False)
            | Q(status__in=EXPORT_JOB_RUNNING_STATUSES)
        )

    class Meta:
        indexes = [
            models.Index(fields=["expires_at", "user", "status"]),
        ]
