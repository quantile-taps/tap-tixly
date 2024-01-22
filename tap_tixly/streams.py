"""Stream type classes for tap-tixly."""

from __future__ import annotations

import sys
import typing as t

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_tixly.client import TixlyStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources


class CustomersStream(TixlyStream):
    """This stream fetches all customers data."""

    name = "customers"
    path = "/customers"
    primary_keys = ["Id"]
    replication_key = "_updated_at"

    schema = th.PropertiesList(
        th.Property("Id", th.StringType),
        th.Property("Gender", th.StringType),
        th.Property("Name", th.StringType),
        th.Property("FirstName", th.StringType),
        th.Property("Edited", th.DateTimeType),
        th.Property("_updated_at", th.DateTimeType),
    ).to_dict()