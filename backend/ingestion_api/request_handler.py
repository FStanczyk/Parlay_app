import requests
import logging
import time
from typing import Optional, Dict, Any, Callable
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class RequestHandler:
    def __init__(
        self, max_retries: int = 3, timeout: float = 30.0, backoff_factor: float = 1.0
    ):
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor

    def _log_error(
        self, attempt: int, url: str, error: Exception, context: Optional[str] = None
    ):
        error_msg = f"Request failed (attempt {attempt}/{self.max_retries})"
        if context:
            error_msg += f" - {context}"
        error_msg += f" - URL: {url}"
        error_msg += f" - Error: {type(error).__name__}: {str(error)}"

        if attempt < self.max_retries:
            logger.warning(error_msg)
        else:
            logger.error(error_msg)

    def _should_retry(self, error: Exception) -> bool:
        if isinstance(error, HTTPError):
            response = error.response
            if response is None:
                return True
            status_code = response.status_code
            return status_code >= 500 or status_code == 429
        elif isinstance(error, (Timeout, ConnectionError)):
            return True
        elif isinstance(error, RequestException):
            return True
        return False

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> requests.Response:
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Making request (attempt {attempt}/{self.max_retries}): {url}"
                )

                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    stream=stream,
                    **kwargs,
                )
                response.raise_for_status()

                if attempt > 1:
                    logger.info(f"Request succeeded on attempt {attempt}: {url}")

                return response

            except HTTPError as e:
                last_exception = e
                if not self._should_retry(e):
                    self._log_error(attempt, url, e, "HTTP error - not retrying")
                    raise
                self._log_error(attempt, url, e, "HTTP error")

            except (Timeout, ConnectionError) as e:
                last_exception = e
                self._log_error(attempt, url, e, "Connection/Timeout error")

            except RequestException as e:
                last_exception = e
                self._log_error(attempt, url, e, "Request error")

            except Exception as e:
                last_exception = e
                self._log_error(attempt, url, e, "Unexpected error")
                raise

            if attempt < self.max_retries:
                wait_time = self.backoff_factor * (2 ** (attempt - 1))
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        logger.error(f"All {self.max_retries} attempts failed for URL: {url}")
        raise last_exception

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Any:
        response = self.get(url, params=params, headers=headers, stream=False, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON response from {url}: {str(e)}")
            raise


req = RequestHandler()
