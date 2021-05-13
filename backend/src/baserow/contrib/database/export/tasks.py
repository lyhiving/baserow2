from baserow.config.celery import app

from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.export.models import ExportJob


@app.task(bind=True)
def run_export_job(self, export_job_id):
    job = ExportJob.objects.get(id=export_job_id)
    ExportHandler().run_export_job(job)
