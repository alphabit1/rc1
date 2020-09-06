FROM python:3.8

WORKDIR /DataCollector

COPY ./requirements.txt /DataCollector
RUN pip install -r requirements.txt

COPY ./ /DataCollector

CMD ["python", "src/main.py"]