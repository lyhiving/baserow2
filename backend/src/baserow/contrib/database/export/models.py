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


class ExportJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    # An export job might be for just a table and not a particular view of that table
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
    progress_percentage = models.FloatField(default=0.0)
    export_options = JSONField()

    def is_cancelled_or_expired(self):
        return self.status in [EXPORT_JOB_CANCELLED_STATUS, EXPORT_JOB_EXPIRED_STATUS]

    @staticmethod
    def unfinished_jobs(user):
        return ExportJob.objects.filter(user=user).filter(
            status__in=[EXPORT_JOB_PENDING_STATUS, EXPORT_JOB_EXPORTING_STATUS]
        )

    @staticmethod
    def jobs_requiring_cleanup(current_time):
        return ExportJob.objects.filter(expires_at__lte=current_time).filter(
            Q(exported_file_name__isnull=False)
            | Q(status__in=[EXPORT_JOB_PENDING_STATUS, EXPORT_JOB_EXPORTING_STATUS])
        )

    class Meta:
        indexes = [
            models.Index(fields=["expires_at", "user", "status"]),
        ]
