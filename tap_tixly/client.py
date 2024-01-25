from typing import Iterable
import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream
from urllib.parse import parse_qsl


class TixlyPaginator(BaseHATEOASPaginator):
    """Fetches the next url from the response."""
    def get_next_url(self, response):
        data = response.json()
        return data.get("Next")


class TixlyStream(RESTStream):
    """Tixly stream class."""
    records_jsonpath = "$.Data[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["url_base"]

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth_token"),
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {
            "Content-Type": "application/json",
        }
        return headers

    def get_new_paginator(self) -> TixlyPaginator:
        return TixlyPaginator()

    def get_url_params(self, context, next_page_token):
        params = {
            "pageSize": 500,
        }

        # Next page token is a URL, so we can to parse it to extract the query string
        if next_page_token:
            params.update(parse_qsl(next_page_token.query))

        if self.replication_key:
            start_time = self.get_starting_timestamp(context)
            start_time_fmt = start_time.strftime("%Y-%m-%dT%H:%M:%SZ") if start_time else None
            params["DateFrom"] = start_time_fmt

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())