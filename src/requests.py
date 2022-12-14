import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

headers = {
    "accept": "application/json, text/html",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
}


class ServerUnavailableError(Exception):
    """
    General error on http requests
    """
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class ServerResponseError(Exception):
    """
    Response status code not 200
    """
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


async def make_request(
    method: str, url: str, data: dict[str, Any] = None, params: dict[str, Any] = None
) -> dict[str, Any] | None:
    """
    Make async http request
    :param params:
    :param method:
    :param url:
    :param data:
    :return: json like dict object
    """
    attempts = 0
    while attempts < 3:
        attempts += 1
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method=method, url=url, headers=headers, json=data, params=params)
                if response.status_code != 200:
                    raise ServerResponseError(f"Error status code: {response.status_code}")
                return response.json()
            except Exception as err:
                logger.error(f"Error making {method.upper()} '{url}' request: {type(err)} {str(err)}")
        await asyncio.sleep(5.0)

    raise ServerUnavailableError(f"Failed connect to server url: {url}")
