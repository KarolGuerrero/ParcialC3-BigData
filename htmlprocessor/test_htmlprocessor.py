from unittest.mock import patch, MagicMock
from htmlprocessor import handler

HTML_FAKE = """
<html>
  <body>
    <a href="/politica/nota1">Titular importante de política</a>
    <a href="/deportes/nota2">Gran victoria en el fútbol</a>
  </body>
</html>
"""

@patch("htmlprocessor.boto3.client")
def test_handler_extraction_and_upload(mock_boto_client):
    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {
        'Body': MagicMock(read=lambda: HTML_FAKE.encode("utf-8"))
    }
    mock_s3.put_object.return_value = {}  # Simula éxito en carga a S3
    mock_boto_client.return_value = mock_s3

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

    result = handler(fake_event, None)

    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] == "ok"
    assert "archivo_procesado" in result
    assert "salida" in result
    assert result["archivo_procesado"] == "headlines/raw/eltiempo-2025-06-09.html"
    assert result["salida"].endswith("noticias.csv")
