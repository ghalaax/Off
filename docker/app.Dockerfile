FROM python:3.7

RUN apt-get update && apt-get install -y \
    gettext \
    libgettextpo-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH="/off"
ENV DJANGO_SETTINGS_MODULE="off.settings"
ADD docker/aliases /usr/sbin/bashrc_alias.sh
RUN cat /usr/sbin/bashrc_alias.sh >> ~/.bashrc

WORKDIR /off

