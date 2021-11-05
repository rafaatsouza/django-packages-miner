FROM python:3.9.7-slim
WORKDIR /src
COPY *.py /src/
RUN pip install requests python-gitlab PyGithub
CMD ["main.py"]
ENTRYPOINT ["python"]