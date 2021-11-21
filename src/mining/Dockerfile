FROM python:3.9.9-slim
WORKDIR /src
COPY *.py /src/
RUN apt-get clean && apt-get update -y && apt-get install -y git
RUN pip install requests python-gitlab PyGithub GitPython pandas
CMD ["main.py"]
ENTRYPOINT ["python"]