FROM python:3.9.9-slim

RUN apt-get clean && apt-get update -y && apt-get install -y git

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm requirements.txt

WORKDIR /src
COPY *.py /src/

CMD ["main.py"]
ENTRYPOINT ["python"]