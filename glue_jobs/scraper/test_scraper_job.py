import pytest
from unittest.mock import patch, MagicMock
from scraper_job import fetch_and_store, today, bucket

@patch('scraper_job.s3.put_object')
@patch('scraper_job.requests.get')
def test_fetch_and_store_success(mock_get, mock_put_object):
    # Simula respuesta exitosa de requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Headline content</html>"
    mock_get.return_value = mock_response

    # Llamar a la función
    fetch_and_store("https://fakeurl.com", "testsource")

    # Validar que requests.get fue llamado correctamente
    mock_get.assert_called_once_with("https://fakeurl.com", headers={"User-Agent": "Mozilla/5.0"})

    # Validar que s3.put_object fue llamado con los parámetros esperados
    expected_key = f'headlines/raw/testsource-{today}.html'
    mock_put_object.assert_called_once_with(
        Bucket=bucket,
        Key=expected_key,
        Body=mock_response.text.encode('utf-8'),
        ContentType='text/html'
    )

@patch('scraper_job.s3.put_object')
@patch('scraper_job.requests.get')
def test_fetch_and_store_failure(mock_get, mock_put_object):
    # Simula respuesta fallida
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    fetch_and_store("https://fakeurl.com", "testsource")

    # put_object no debe ser llamado si status_code != 200
    mock_put_object.assert_not_called()
