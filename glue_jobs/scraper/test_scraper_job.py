# glue_jobs/scraper/test_scraper_job.py

import pytest
from unittest.mock import patch, MagicMock
from scraper_job import fetch_and_store, bucket, today


@patch("scraper_job.s3.put_object")
@patch("scraper_job.requests.get")
def test_fetch_and_store_success(mock_get, mock_put_object):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>OK</body></html>"
    mock_get.return_value = mock_response

    fetch_and_store("http://fakeurl.com", "testsource")

    expected_key = f'headlines/raw/testsource-{today}.html'
    mock_put_object.assert_called_once_with(
        Bucket=bucket,
        Key=expected_key,
        Body=mock_response.text.encode('utf-8'),
        ContentType='text/html'
    )


@patch("scraper_job.requests.get")
def test_fetch_and_store_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with patch("builtins.print") as mock_print:
        fetch_and_store("http://fakeurl.com", "testsource")
        mock_print.assert_called_with("Error descargando testsource: 404")
