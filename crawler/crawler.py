import boto3
from botocore.exceptions import ClientError

CRAWLER_NAME = "noticias_crawler"
def handler(event=None, context=None):
    glue = boto3.client("glue")
    try:
        glue.start_crawler(Name=CRAWLER_NAME)
        return {
            "status": "ok",
            "mensaje": f"Crawler '{CRAWLER_NAME}' ejecutado correctamente",
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'CrawlerRunningException':
            return {
                "status": "error",
                "mensaje": f"El crawler '{CRAWLER_NAME}' ya está en ejecución.",
            }
        else:
            return {
                "status": "error",
                "mensaje": str(e),
            }
