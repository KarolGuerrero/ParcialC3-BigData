import pytest
from unittest.mock import patch, MagicMock
from app import download_and_upload

@patch("app.requests.get")
@patch("app.boto3.client")
def test_download_and_upload_success(mock_boto_client, mock_requests_get):
    # Mock de la respuesta HTTP
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"
    mock_requests_get.return_value = mock_response

    # Mock del cliente S3
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    # Ejecutar la función
    result = download_and_upload("https://example.com", "example")

    # Verificaciones
    assert "example saved to headlines/raw/example-" in result
    mock_requests_get.assert_called_once()
    mock_s3.put_object.assert_called_once()