FROM python:3.9.7-slim
COPY *.py /
RUN pip install requests python-gitlab PyGithub
CMD ["main.py"]
ENTRYPOINT ["python"]