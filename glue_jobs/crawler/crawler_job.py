import boto3

def start_noticias_crawler():
    client = boto3.client('glue')
    response = client.start_crawler(Name='noticias_crawler')
    print("Crawler iniciado:", response)
    return response
