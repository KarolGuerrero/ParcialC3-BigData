import pytest
from unittest.mock import patch, MagicMock
from crawler_job import start_noticias_crawler

@patch('crawler_job.boto3.client')
def test_start_noticias_crawler(mock_boto_client):
    # Mock del cliente de Glue
    mock_glue = MagicMock()
    mock_glue.start_crawler.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

    mock_boto_client.return_value = mock_glue

    response = start_noticias_crawler()

    # Verificar que se creó el cliente de Glue
    mock_boto_client.assert_called_once_with('glue')

    # Verificar que se llamó start_crawler con el nombre correcto
    mock_glue.start_crawler.assert_called_once_with(Name='noticias_crawler')

    # Verificar la respuesta
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
