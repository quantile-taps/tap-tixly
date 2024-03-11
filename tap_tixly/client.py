from typing import Iterable

import pendulum
import requests

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

from urllib.parse import urlparse, parse_qsl, parse_qs


class TixlyPaginator(BaseHATEOASPaginator):
    """Fetches the next url from the response."""
    def get_next_url(self, response):
        data = response.json()
        return data.get("Next")
    
class TixlyEventSalesPaginator(TixlyPaginator):
    """Custom TixlyPaginator for the event sales stream."""
    def get_next_url(self, response):
        data = response.json()

        # Get the next url from the response
        next_url = data.get("Next")

        # If there is a next url, we return it
        if next_url:
            return next_url

        # If there is no next url, we check if we have reached the end of the data

        # Extract the url params from the response url
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)

        # Lower case the keys in the query_params
        query_params = {k.lower(): v for k, v in query_params.items()}

        # Select the `SoldTo` url param and convert it to a pendulum date
        sold_to = pendulum.parse(query_params.get("soldto")[0])

        # If the `SoldTo` date is less than or equal to today's date, we have not yet reached the end of the data
        if sold_to <= pendulum.today():

            # Construct the next url: SoldFrom is the same as the previous SoldTo, and SoldTo is the previous SoldTo plus 1 year
            next_sold_from = sold_to.to_date_string()
            next_sold_to = sold_to.add(months=1).to_date_string()

            next_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?pageSize=500&SoldFrom={next_sold_from}&SoldTo={next_sold_to}"

            return next_url
        
        else:
            return None


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