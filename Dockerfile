FROM python:3.13-slim
MAINTAINER wutingfeng@outlook.com

ENV PYTHONUNBUFFERED True

RUN apt-get update
RUN apt-get -y install wget dpkg fonts-ipafont-gothic fonts-ipafont-mincho
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

RUN groupadd -r unprivilegeduser && useradd -r -g unprivilegeduser unprivilegeduser
USER unprivilegeduser
WORKDIR /home/unprivilegeduser

COPY --chown=unprivilegeduser:unprivilegeduser requirements.txt .
RUN python3 -m venv venv
RUN venv/bin/python3 -m pip install --upgrade pip
RUN venv/bin/python3 -m pip install --no-cache-dir -r requirements.txt

COPY --chown=unprivilegeduser:unprivilegeduser takeashot.py .
ENTRYPOINT ["venv/bin/python3", "takeashot.py"]
CMD ["--help"]
