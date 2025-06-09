import requests
from datetime import datetime
import boto3

s3 = boto3.client('s3')
BUCKET = 'parcial-save-html-scrapper'


def download_and_upload(url, source_name):
    """Descarga HTML desde una URL y lo guarda en S3."""
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"headlines/raw/{source_name}-{today}.html"
        s3.put_object(
            Bucket=BUCKET,
            Key=filename,
            Body=response.text.encode('utf-8'),
            ContentType='text/html'
        )
        return f"{source_name} saved to {filename}"
    return f"Failed to fetch {source_name}: {response.status_code}"


def handler(event=None, context=None):
    """Handler principal que descarga HTML de varias fuentes."""
    logs = []
    logs.append(
        download_and_upload("https://www.eltiempo.com/", "eltiempo")
    )
    logs.append(
        download_and_upload("https://www.elespectador.com/", "elespectador")
    )
    return {"result": logs}
