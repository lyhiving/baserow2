import uuid

from djqscsv import write_csv

from baserow.config.celery import app
from os.path import join


@app.task(bind=True)
def export_view(self, user_id, view_id, export_type):
    export_view_inner(user_id, view_id, export_type)


def export_view_inner(user_id, view_id, export_type):
    from django.conf import settings
    from baserow.contrib.database.export.handler import ExportHandler
    from django.contrib.auth import get_user_model
    from baserow.contrib.database.views.models import GridView
    from baserow.contrib.database.api.views.grid.grid_view_handler import (
        GridViewHandler,
    )
    from baserow.contrib.database.views.handler import ViewHandler
    from django.core.files.storage import default_storage

    User = get_user_model()
    view = ViewHandler().get_view(view_id, GridView)
    user = User.objects.get(id=user_id)
    rows = GridViewHandler().get_rows(
        user, view, search=None, exclude_hidden_fields=True
    )
    assert export_type == "csv"
    filename = str(uuid.uuid4()) + ".csv"
    url = join(settings.EXPORT_FILES_DIRECTORY, filename)
    print("Saving to url")
    with default_storage.open(url, "wb") as csv_file:
        write_csv(rows, csv_file)
    ExportHandler().finished_export_job(user_id, view_id, export_type, url)
