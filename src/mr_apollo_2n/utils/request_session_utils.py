from typing import Dict, List, Optional

import requests  # type: ignore
from requests.exceptions import (ConnectionError, HTTPError,  # type: ignore
                                 Timeout)
from retry import retry  # type: ignore

from mr_apollo_2n.utils.base_class import BaseClass


class RequestSession(BaseClass):
    def __init__(
        self,
        method: Optional[str] = "GET",
        request_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        allow_redirects: Optional[bool] = True,
        update_headers: Optional[bool] = True,
        retry_supported_codes: Optional[List[int]] = None,
        retry_delay: Optional[int] = 180,
        retry_tries: Optional[int] = 3,
    ):
        """
        Request Session class, used to create a session and execute requests.

        Parameters
        ----------
        method : str
                                        The request method to use.
        request_data : Optional[Dict], optional
                                        The request data to use (default is {}).
        headers : Optional[Dict], optional
                                        The request headers to use (default is {}).
        allow_redirects : Optional[bool], optional
                                        Whether to allow redirects or not (default is True).
        update_headers : Optional[bool], optional
                                        Whether to update the headers or not (default is True).
        retry_supported_codes : List[int], optional
                                        The list of supported codes to retry (default is [429, 503]).
        retry_delay : Optional[int], optional
                                        Secs to wait between retries (default is 180).
        retry_tries : Optional[int], optional
                                        Number of retries (default is 3).
        """
        super().__init__(logger_name=__name__)
        self.retry_delay = retry_delay
        self.retry_tries = retry_tries
        self.headers = headers if headers is not None else {}
        self.method = method
        self.request_data = request_data if request_data is not None else {}
        self.allow_redirects = allow_redirects
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        if update_headers:
            self.session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cache-Control": "max-age=0",
                    "Upgrade-Insecure-Requests": "1",
                }
            )
        if retry_supported_codes is None:
            self.retry_supported_codes = [
                429,
                503,
            ]  # Too Many Requests, Service Unavailable
        self.exec_request = self._create_exec_request_with_retry()

    def _create_exec_request_with_retry(self):
        @retry(
            delay=self.retry_delay, tries=self.retry_tries, exceptions=ConnectionError
        )
        def exec_request(url: str) -> Optional[str]:
            try:
                response = self.session.request(
                    self.method,
                    url,
                    data=self.request_data,
                    allow_redirects=self.allow_redirects,
                )
                response.raise_for_status()

                if response.status_code in self.retry_supported_codes:
                    self.logger.info(
                        f"Retry due to response code: {response.status_code}"
                    )
                    raise ConnectionError(
                        f"Retrying due to response code: {response.status_code}"
                    )
                return response.text
            except (HTTPError, ConnectionError, Timeout) as err:
                self.logger.error(f"Connection error when connecting to {url}: {err}")
                raise ConnectionError(f"Error attempting to connect to {url}: {err}")
            except Exception as err:
                self.logger.error(
                    f"Unexpected error processing request to {url}: {err}"
                )
                raise Exception(f"Unexpected error processing request to {url}: {err}")

        return exec_request
