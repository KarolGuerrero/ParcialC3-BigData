import requests
import boto3
from datetime import datetime


class MitulaScraper:
    """Clase para realizar scraping de Mitula y subir resultados a S3."""

    def __init__(self, base_url="https://casas.mitula.com.co/casas/bogota"):
        """Inicializa el scraper con la URL base y las cabeceras."""
        self.base_url = base_url
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_search_results(self, search_url, num_pages=5):
        """Obtiene las páginas de resultados y las sube a S3."""
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'parcial-save-html-scrapper'

        for page in range(1, num_pages + 1):
            page_url = f"{search_url}?page={page}"
            print(f"Scraping page {page}: {page_url}")

            try:
                response = self.session.get(page_url, timeout=10)
                response.raise_for_status()

                # Subir el contenido HTML de la página a S3
                file_name = (
                    f'{datetime.now().strftime("%Y%m%d")}/page_{page}.html'
                )
                print(f"Uploading {file_name} to S3")
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=file_name,
                    Body=response.text
                )

            except requests.RequestException as e:
                print(f"Error scraping page {page}: {e}")


def app(event, ctx):
    """Función principal que ejecuta el scraper."""
    scraper = MitulaScraper()
    search_url = "https://casas.mitula.com.co/casas/bogota"
    scraper.get_search_results(search_url, num_pages=10)
    
    print('Scrapper completado')
    
    return {
        'statusCode': 200,
    }
