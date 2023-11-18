FROM python:3.8
RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code/
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
ENV PYTHONUNBUFFERED=1
CMD [ "python", "./main.py" ]
