from bs4 import BeautifulSoup
import boto3
from datetime import datetime
import pandas as pd
import io

s3 = boto3.client('s3')
bucket = 'parcial-save-scrapper'
today = datetime.now()

fuentes = ['eltiempo', 'elespectador']
resultados = []

for fuente in fuentes:
    key = f"headlines/raw/{fuente}-{today.strftime('%Y-%m-%d')}.html"
    obj = s3.get_object(Bucket=bucket, Key=key)
    contenido = obj['Body'].read().decode('utf-8')
    soup = BeautifulSoup(contenido, 'html.parser')

    for enlace in soup.find_all('a'):
        titulo = enlace.get_text(strip=True)
        href = enlace.get('href')
        if titulo and href:
            resultados.append({
                'periodico': fuente,
                'fecha': today.strftime('%Y-%m-%d'),
                'categoria': '',  # Este valor debe parsearse con lógica específica del sitio
                'titulo': titulo,
                'url': href
            })

# Guardar como CSV en S3 particionado
df = pd.DataFrame(resultados)
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)

s3.put_object(
    Bucket=bucket,
    Key=f"headlines/final/periodico={fuente}/year={today.year}/month={today.month}/day={today.day}/noticias.csv",
    Body=csv_buffer.getvalue(),
    ContentType='text/csv'
)