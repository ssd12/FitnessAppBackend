#base image
FROM python:2.7

#label maintainer
LABEL maintainer ssd

#run pip and install requirements
RUN pip install --upgrade pip

COPY ./application.py /app/
COPY ./DatabaseUtilities.py /app/

WORKDIR /app/

COPY requirements.txt .

#install requirements
RUN pip install -r requirements.txt
