FROM gitpod/workspace-full:latest

USER gitpod

RUN pip3 install --no-warn-script-location \
    -r /workspace/baserow/backend/requirements/base.txt \
    -r /workspace/baserow/backend/requirements/dev.txt
COPY ./premium/backend ./backend/plugins/premium
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/workspace/baserow/backend/src:/workspace/baserow/backend/plugins/premium/src
ENV DJANGO_SETTINGS_MODULE='baserow.config.settings.dev'
