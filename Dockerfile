FROM python:3.10

ADD . ./


RUN pip install -r requirements.txt
ENV PATH="/opt/gtk/bin:$env/credentials.env"

CMD ["python3", "./main.py"]
