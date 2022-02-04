FROM registry.access.redhat.com/ubi8/python-39

COPY requirements.txt .
COPY main.py .

RUN pip3 install -r requirements.txt

USER 1000

CMD ["python", "main.py"]