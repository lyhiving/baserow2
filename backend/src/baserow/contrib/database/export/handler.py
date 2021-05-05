from baserow.contrib.database.export.exceptions import ExportAlreadyRunningException
from baserow.contrib.database.export.models import (
    ExportJob,
    EXPORT_JOB_EXPORTING_STATUS,
)
from baserow.contrib.database.export.tasks import export_view


class ExportHandler:
    def get_export_job(self, user, view, job_type):
        try:
            return ExportJob.objects.get(user=user, view=view, type=job_type)
        except ExportJob.DoesNotExist:
            return ExportJob(user=user, view=view, type=job_type, status="ready")

    def start_export_job(self, user, view, job_type):
        self.cleanup_job(user, view, job_type)

        job = ExportJob.objects.create(
            user=user,
            view=view,
            type=job_type,
            status=EXPORT_JOB_EXPORTING_STATUS,
        )
        export_view.delay(user.id, view.id, job_type)
        return job

    def cleanup_job(self, user, view, job_type):
        try:
            job = ExportJob.objects.filter(user=user, view=view, type=job_type).get()
            if job.download_url is not None or job.is_exporting():
                # TODO clean up file from storage
                pass
            job.delete()
        except ExportJob.DoesNotExist:
            pass

    def finished_export_job(self, user_id, view_id, export_type, url):
        job = ExportJob.objects.get(user_id=user_id, view_id=view_id, type=export_type)
        job.status = "completed"
        job.download_url = url
        job.save()
