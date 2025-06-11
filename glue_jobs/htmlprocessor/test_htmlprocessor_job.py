import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from htmlprocessor_job import parse_html_to_csv, bucket

@patch('htmlprocessor_job.s3.put_object')
@patch('htmlprocessor_job.s3.get_object')
def test_parse_html_to_csv(mock_get_object, mock_put_object):
    # Fecha fija para prueba
    test_date = datetime(2024, 5, 10)

    # HTML de prueba
    html = """
    <html>
        <body>
            <a href="https://noticia1.com">Noticia Uno</a>
            <a href="https://noticia2.com">Noticia Dos</a>
        </body>
    </html>
    """
    # Mock S3 get_object
    mock_get_object.return_value = {
        'Body': MagicMock(read=MagicMock(return_value=html.encode('utf-8')))
    }

    # Ejecutar función
    parse_html_to_csv(today=test_date)

    # Verificar que get_object fue llamado dos veces (una por fuente)
    assert mock_get_object.call_count == 2

    # Verificar que put_object fue llamado dos veces (una por fuente)
    assert mock_put_object.call_count == 2

    # Verificar el contenido del primer archivo CSV generado
    args, kwargs = mock_put_object.call_args
    csv_body = kwargs['Body']
    assert "periodico,fecha,categoria,titulo,url" in csv_body
    assert "eltiempo,2024-05-10,,Noticia Uno,https://noticia1.com" in csv_body or \
           "elespectador,2024-05-10,,Noticia Uno,https://noticia1.com" in csv_body
