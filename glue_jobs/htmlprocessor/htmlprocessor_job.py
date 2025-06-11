import io
from datetime import datetime
import boto3
import pandas as pd
from bs4 import BeautifulSoup

s3 = boto3.client('s3')
bucket = 'parcial-save-scrapper'

def parse_html_to_csv(today=None):
    if today is None:
        today = datetime.now()
    fuentes = ['eltiempo', 'elespectador']

    for fuente in fuentes:
        key = f"headlines/raw/{fuente}-{today.strftime('%Y-%m-%d')}.html"
        obj = s3.get_object(Bucket=bucket, Key=key)
        contenido = obj['Body'].read().decode('utf-8')
        soup = BeautifulSoup(contenido, 'html.parser')

        resultados = []

        for enlace in soup.find_all('a'):
            titulo = enlace.get_text(strip=True)
            href = enlace.get('href')
            if titulo and href:
                resultados.append({
                    'periodico': fuente,
                    'fecha': today.strftime('%Y-%m-%d'),
                    'categoria': '',
                    'titulo': titulo,
                    'url': href
                })

        df = pd.DataFrame(resultados)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        output_key = (
            f"headlines/final/periodico={fuente}/year={today.year}/"
            f"month={today.month}/day={today.day}/noticias.csv"
        )

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
