FROM python:3.7
ADD . /source
WORKDIR /source
RUN pip install -r requirements.txt
