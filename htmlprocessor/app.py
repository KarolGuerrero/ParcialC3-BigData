import boto3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client('s3')


def handler(event, context):
    """Procesa archivos HTML desde S3, extrae titulares y guarda como CSV."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        if not key.endswith('.html'):
            continue

        # Detectar periódico
        if 'eltiempo' in key:
            periodico = 'eltiempo'
        elif 'elespectador' in key:
            periodico = 'elespectador'
        else:
            periodico = 'desconocido'

        # Obtener la fecha desde el nombre del archivo
        date_part = key.split('/')[-1].replace('.html', '').split('-')[-3:]
        yyyy, mm, dd = date_part

        # Descargar el archivo HTML desde S3
        response = s3.get_object(Bucket=bucket, Key=key)
        html = response['Body'].read().decode('utf-8')

        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # Extraer enlaces y titulares
        for link in soup.find_all('a'):
            href = link.get('href')
            title = link.get_text(strip=True)
            if not href or not title or len(title) < 10:
                continue

            categoria = href.strip('/').split('/')[0] if '/' in href else 'general'

            articles.append({
                'categoria': categoria,
                'titular': title,
                'enlace': href
            })

        # Guardar resultados como CSV
        df = pd.DataFrame(articles)
        csv_buffer = df.to_csv(index=False).encode('utf-8')

        output_key = (
            f"headlines/final/periodico={periodico}/year={yyyy}/"
            f"month={mm}/day={dd}/noticias.csv"
        )

        s3.put_object(Bucket=bucket, Key=output_key, Body=csv_buffer)

        return {
            "status": "ok",
            "archivo_procesado": key,
            "salida": output_key
        }
