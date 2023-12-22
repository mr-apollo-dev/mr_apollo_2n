from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError  # type: ignore

from mr_apollo_2n.utils.request_session_utils import RequestSession


def test_exec_request_success():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.text = "Success"

    with patch("requests.Session.request", return_value=mock_response):
        session = RequestSession("GET", {}, {}, True, retry_delay=1, retry_tries=1)
        assert session.exec_request("http://example.com") == "Success"


def test_exec_request_connection_error():
    with patch(
        "requests.Session.request", side_effect=ConnectionError("Connection failed")
    ):
        session = RequestSession("GET", {}, {}, True, retry_delay=1, retry_tries=1)
        with pytest.raises(ConnectionError):
            session.exec_request("http://example.com")


def test_exec_request_retry_supported_codes():
    for status_code in [429, 503]:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError(
            "Error", response=Mock(status_code=status_code)
        )

        with patch("requests.Session.request", return_value=mock_response):
            session = RequestSession("GET", {}, {}, True, retry_delay=1, retry_tries=1)
            with pytest.raises(ConnectionError):
                session.exec_request("http://example.com")


def test_exec_request_unexpected_exception():
    with patch("requests.Session.request", side_effect=Exception("Unexpected error")):
        session = RequestSession("GET", {}, {}, True, retry_delay=1, retry_tries=1)
        with pytest.raises(Exception):
            session.exec_request("http://example.com")
