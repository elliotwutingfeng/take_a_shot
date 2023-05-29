FROM python:3.11-slim
MAINTAINER wutingfeng@outlook.com

ENV PYTHONUNBUFFERED True

RUN apt-get update
RUN apt-get -y install wget dpkg
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

RUN apt-get -y install fonts-ipafont-gothic fonts-ipafont-mincho

ADD requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ADD takeashot.py /tmp/
ENTRYPOINT ["python", "/tmp/takeashot.py"]
CMD ["--help"]
