from botocore.exceptions import ClientError
import boto3
from unittest.mock import patch, MagicMock
from crawler import handler

@patch("crawler.boto3.client")
def test_handler_crawler_already_running(mock_boto_client):
    mock_glue = MagicMock()
    error_response = {
        "Error": {"Code": "CrawlerRunningException", "Message": "Crawler is running"}
    }
    mock_glue.start_crawler.side_effect = ClientError(error_response, "StartCrawler")
    mock_boto_client.return_value = mock_glue

    result = handler()

    assert result["status"] == "error"
    assert "ya está en ejecución" in result["mensaje"]

