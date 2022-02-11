FROM registry.access.redhat.com/ubi8/python-39

COPY requirements.txt .
COPY main.py .
COPY logutil.py .
COPY device_info.py .
COPY notification.py .

RUN pip3 install -r requirements.txt

USER 1000

CMD ["python", "main.py"]