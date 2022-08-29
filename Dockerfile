FROM python:3.9.4-alpine

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV TZ=Asia/Singapore
ENV FLASK_APP=/root/azure/app.py
COPY azure /root/azure
COPY requirements.txt ./
RUN apk --no-cache add gcc g++ libffi-dev libressl-dev &&\
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt &&\
    apk del gcc g++ libffi-dev libressl-dev
COPY . .

CMD ["sh", "-c", "flask initdb ; python /root/azure/app.py"]
