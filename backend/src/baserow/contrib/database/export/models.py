from django.contrib.auth import get_user_model
from django.db import models

from baserow.contrib.database.export.exceptions import EXPORT_JOB_ERRORS

User = get_user_model()

EXPORT_JOB_EXPORTING_STATUS = "exporting"

EXPORT_JOB_STATUS_CHOICES = [
    ("ready", "ready"),
    (EXPORT_JOB_EXPORTING_STATUS, EXPORT_JOB_EXPORTING_STATUS),
    ("complete", "complete"),
    ("failed", "failed"),
]

EXPORT_JOB_TYPES = [
    ("csv", "csv"),
]


class ExportJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view = models.ForeignKey("database.View", on_delete=models.CASCADE)
    status = models.TextField(choices=EXPORT_JOB_STATUS_CHOICES)
    type = models.TextField(choices=EXPORT_JOB_STATUS_CHOICES)
    download_url = models.URLField(null=True, blank=True)
    error = models.TextField(choices=EXPORT_JOB_ERRORS, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def is_exporting(self):
        return self.status == EXPORT_JOB_EXPORTING_STATUS

    class Meta:
        unique_together = [["user"], ["view"], ["type"]]
        indexes = [
            models.Index(fields=["user", "view", "type"]),
        ]
