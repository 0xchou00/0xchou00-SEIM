FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/0xchou00

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY agent ./agent
COPY rules ./rules
COPY web ./web
COPY lab ./lab

RUN chmod +x /opt/0xchou00/lab/start-siem.sh

EXPOSE 8000

CMD ["/opt/0xchou00/lab/start-siem.sh"]
