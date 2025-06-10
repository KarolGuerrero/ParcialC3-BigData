import requests
from datetime import datetime
import boto3

s3 = boto3.client('s3')
bucket = 'parcial-save-scrapper'
today = datetime.now().strftime('%Y-%m-%d')

def fetch_and_store(url, source):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code == 200:
        key = f'headlines/raw/{source}-{today}.html'
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=r.text.encode('utf-8'),
            ContentType='text/html'
        )
        print(f"{source} guardado en {key}")
    else:
        print(f"Error descargando {source}: {r.status_code}")

fetch_and_store("https://www.eltiempo.com/", "eltiempo")
fetch_and_store("https://www.elespectador.com/", "elespectador")