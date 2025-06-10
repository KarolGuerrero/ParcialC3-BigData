import pytest
from unittest.mock import patch, MagicMock
from app import handler

# Simular un HTML básico con titulares
HTML_FAKE = """
<html>
  <body>
    <a href="/deportes/futbol">Título de Fútbol</a>
    <a href="/politica">Política actual</a>
    <a href="/cultura">Cultura y sociedad</a>
  </body>
</html>
"""

@patch("app.boto3.client")
def test_handler_extraction_and_upload(mock_boto_client):
    # Preparar mocks
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    # Simular get_object que devuelve el HTML
    mock_s3.get_object.return_value = {
        'Body': MagicMock(read=lambda: HTML_FAKE.encode("utf-8"))
    }

    # Evento simulado de S3
    fake_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "fake-bucket"},
                    "object": {"key": "headlines/raw/eltiempo-2025-06-09.html"}
                }
            }
        ]
    }

    # Ejecutar handler
    result = handler(fake_event, None)

    # Afirmaciones
    assert result["status"] == "ok"
    assert "noticias.csv" in result["salida"]
    mock_s3.get_object.assert_called_once()
    mock_s3.put_object.assert_called_once()

    # Validar que el CSV generado contiene los títulos
    args, kwargs = mock_s3.put_object.call_args
    csv_content = kwargs["Body"].decode("utf-8")
    assert "Título de Fútbol" in csv_content
    assert "politica" in csv_content