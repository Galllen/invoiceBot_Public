FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    fonts-liberation \
    fonts-dejavu \
    fontconfig \
    && fc-cache -f -v \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV INVOICE_TEMPLATE=/app/handlers/invoice.docx
ENV PYTHONUNBUFFERED=1


ENV HOME=/tmp

CMD ["python", "main.py"]