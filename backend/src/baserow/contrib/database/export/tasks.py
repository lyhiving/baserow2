from datetime import timedelta

from baserow.config.celery import app

from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.export.models import ExportJob


# noinspection PyUnusedLocal
@app.task(bind=True)
def run_export_job(self, job_id):
    job = ExportJob.objects.get(id=job_id)
    ExportHandler().run_export_job(job)


# noinspection PyUnusedLocal
@app.task(bind=True)
def clean_up_old_jobs(self):
    ExportHandler().clean_up_old_jobs()


# noinspection PyUnusedLocal
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(timedelta(minutes=1), clean_up_old_jobs.s())
