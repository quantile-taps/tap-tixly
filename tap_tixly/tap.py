"""Tixly tap class."""

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_tixly import streams
from typing import List

STREAM_TYPES = [
    streams.CustomersStream,
    streams.MembershipsStream,
    streams.MembershipsSalesStream,
    streams.EventsStream,
    streams.EventsSalesStream,
]


class TapTixly(Tap):
    """Tixly tap class."""
    name = "tap-tixly"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "url_base",
            th.StringType,
            default="https://crmapi.tixnl.nl/v3",
            description="The base url for the API service for Tixly.",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapTixly.cli()
