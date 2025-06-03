import boto3
import csv
import json
from bs4 import BeautifulSoup
from datetime import datetime

s3_client = boto3.client('s3', "us-east-1")

def extract_property_data(card):
    """Extrae la información relevante de una propiedad desde un elemento HTML."""
    try:
        property_data = {
            "FechaDescarga": datetime.now().strftime('%Y-%m-%d'),
            "Titulo": card.find('span', class_='title').text.strip() if card.find('span', class_='title') else "N/A",
            "Valor": card.find('span', class_='price__actual').text.strip() if card.find('span', class_='price__actual') else "N/A",
            "Ubicacion": card.find('div', class_='listing-card__location-geo').text.strip() if card.find('div', class_='listing-card__location-geo') else "N/A",
            "Area": card.find('div', class_='listing-card__icon__area').find('p').text.strip() if card.find('div', class_='listing-card__icon__area') else "N/A",
            "NumHabitaciones": card.find('div', class_='listing-card__icon__bedrooms').find('p').text.strip() if card.find('div', class_='listing-card__icon__bedrooms') else "N/A",
            "NumBanos": card.find('div', class_='listing-card__icon__bathrooms').find('p').text.strip() if card.find('div', class_='listing-card__icon__bathrooms') else "N/A"
        }
        return property_data
    except Exception as e:
        print(f"Error al extraer datos de una propiedad: {e}")
        return None

def app(event, context):
    """Función Lambda que procesa todos los archivos HTML en el bucket y genera un CSV consolidado."""
    try:
        
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        object_key = event["Records"][0]["s3"]["object"]["key"]
        
        print("Se subio algo")
        
        # Listar todos los archivos HTML en el bucket
        objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="").get('Contents', [])
        
        properties = []
        for obj in objects:
            object_key = obj['Key']
            if object_key.endswith('.html'):
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                html_content = response['Body'].read().decode('utf-8')
                
                # Parsear HTML con BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                property_cards = soup.find_all('div', class_='listing-card__content')
                properties.extend([extract_property_data(card) for card in property_cards if extract_property_data(card) is not None])
        
        if not properties:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": "No se encontraron propiedades en los archivos HTML"})
            }
        
        # Crear el archivo CSV consolidado
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        csv_filename = f"{fecha_actual}.csv"
        csv_content = [["FechaDescarga", "Titulo", "Valor", "Ubicacion", "Area", "NumHabitaciones", "NumBanos"]]

        for prop in properties:
            csv_content.append([prop[col] for col in csv_content[0]])

        # Convertir a CSV en memoria
        csv_data = "\n".join([",".join(row) for row in csv_content])
        
        # Guardar en otro bucket
        output_bucket = "parcial-save-csv"
        output_key = f"{fecha_actual}/{csv_filename}"

        s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=csv_data, ContentType='text/csv')

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "CSV consolidado generado correctamente", "archivo": output_key})
        }

    except Exception as e:
        print(f"Error en la función Lambda: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
