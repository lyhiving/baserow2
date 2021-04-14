FROM baserow_backend:latest

ADD . /premium/backend

ENV PYTHONPATH $PYTHONPATH:/backend/src:/premium/backend/src
ENV ADDITIONAL_APPS=baserow_premium
