FROM python:3.10-slim AS compile-image
WORKDIR /python-docker
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc git libmagic-dev

ENV PYTHONUNBUFFERED 1

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache \
    pip install uwsgi
COPY requirements/fr.txt requirements/fr.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements/fr.txt
COPY requirements/flasks.txt requirements/flasks.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements/flasks.txt


FROM python:3.10-slim AS build-image

WORKDIR /python-docker

# Copy the virtualenv from the compile-image
COPY --from=compile-image /opt/venv /opt/venv
WORKDIR /python-docker

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
# Copy  configuration file
COPY uwsgi.ini uwsgi.ini

COPY config.py .
COPY app.py .
COPY core core/
COPY api api/


EXPOSE 80

CMD uwsgi --ini uwsgi.ini
