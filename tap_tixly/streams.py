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
        th.Property("Id", th.IntegerType),
        th.Property("Title", th.StringType),
        th.Property("Name", th.StringType),
        th.Property("FirstName", th.StringType),
        th.Property("LastNamePrefix", th.StringType),
        th.Property("LastName", th.StringType),
        th.Property("DateOfBirth", th.DateTimeType),
        th.Property("Gender", th.StringType),
        th.Property("AddressOne", th.StringType),
        th.Property("AddressTwo", th.StringType),
        th.Property("ZipCode", th.StringType),
        th.Property("City", th.StringType),
        th.Property("StreetName", th.StringType),
        th.Property("HouseNumber", th.StringType),
        th.Property("HouseExtension", th.StringType),
        th.Property("Country", th.StringType),
        th.Property("LanguageId", th.IntegerType),
        th.Property("Email", th.StringType),
        th.Property("Edited", th.DateTimeType),
        th.Property("_updated_at", th.DateTimeType),
    ).to_dict()

    def post_process(
        self,
        row: dict,
        context: dict,
    ) -> dict:
        """
        We introduce this post process method due to finding the correct replication value.

        The desired replication key exists in either the "Edited" or "Created" column. This
        is because newly added records only contain a "Created" value and not an "Edited"
        value. The "Edited" column contains a null (parsed to None) for newly created records.
        """
        if row["Edited"] == None:
            _updated_at = row["Created"]

        else:
            _updated_at = row["Edited"]

        return {
            **row,
            "_updated_at": _updated_at,
        }



class MembershipsStream(TixlyStream):
    """This stream fetches all memberships data."""

    name = "memberships"
    path = "/memberships"
    primary_keys = ["Id"]

    schema = th.PropertiesList(
        th.Property("Id", th.IntegerType),
        th.Property("Name", th.StringType),
        th.Property("Abbreviation", th.StringType),
        th.Property("Tagline", th.StringType),
        th.Property("ShortDescription", th.StringType),
        th.Property("Description", th.StringType),
        th.Property("Price", th.NumberType),
        th.Property("Vat", th.NumberType),
        th.Property("AvailableOnline", th.BooleanType),
        th.Property("RenewDayOfMonth", th.StringType),
        th.Property("RenewMonthOfYear", th.StringType),
        th.Property("Created", th.DateTimeType),
    ).to_dict()


class MembershipsSalesStream(TixlyStream):
    """This stream fetches all the memberships sales data."""

    name = "memberships-sales"
    path = "/memberships/sales"
    primary_keys = ["Id"]

    schema = th.PropertiesList(
        th.Property("Id", th.IntegerType),
        th.Property("OrderMembershipId", th.IntegerType),
        th.Property("OrderId", th.IntegerType),
        th.Property("MembershipID", th.IntegerType),
        th.Property("CustomerId", th.IntegerType),
        th.Property("Name", th.StringType),
        th.Property("Abbreviation", th.StringType),
        th.Property("Tagline", th.StringType),
        th.Property("ShortDescription", th.StringType),
        th.Property("Description", th.StringType),
        th.Property("Price", th.NumberType),
        th.Property("Vat", th.NumberType),
        th.Property("AvailableOnline", th.BooleanType),
        th.Property("RenewDayOfMonth", th.IntegerType),
        th.Property("RenewMonthOfYear", th.IntegerType),
        th.Property("isCancelled", th.BooleanType),
        th.Property("SkinID", th.IntegerType),
        th.Property("OrganisationID", th.IntegerType),
        th.Property("RenewalType", th.StringType),
        th.Property("Created", th.DateTimeType),
        th.Property("Expires", th.DateTimeType),
    ).to_dict()


class EventsStream(TixlyStream):
    """This stream fetches all the events."""

    name = "events"
    path = "/events"
    primary_keys = ["Id"]

    schema = th.PropertiesList(
        th.Property("Id", th.IntegerType),
        th.Property("Name", th.StringType),
        th.Property("StartDate", th.DateTimeType),
        th.Property("EndDate", th.DateTimeType),
        th.Property("PromoterId", th.IntegerType),
        th.Property("Promoter", th.StringType),
        th.Property("HallId", th.IntegerType),
        th.Property("Hall", th.StringType),
        th.Property("Categories", 
            th.ArrayType(
                th.ObjectType(
                    th.Property("Id", th.IntegerType),
                    th.Property("Name", th.StringType),
                )
        )),
        th.Property("Sold", th.IntegerType),
        th.Property("Capacity", th.IntegerType),
        th.Property("Reserved", th.IntegerType),
        th.Property("Allocated", th.IntegerType),
        th.Property("BlockedAllocated", th.IntegerType),
        th.Property("Vat", th.NumberType),
    ).to_dict()


class EventsSalesStream(TixlyStream):
    """This stream fetches all the events."""

    name = "events-sale"
    path = "/events/sales"
    primary_keys = ["Id"]
    replication_key = "Created"

    schema = th.PropertiesList(
        th.Property("Id", th.IntegerType),
        th.Property("TicketId", th.IntegerType),
        th.Property("EventId", th.IntegerType),
        th.Property("CustomerId", th.IntegerType),
        th.Property("IsAnonymousSale", th.BooleanType),
        th.Property("OrderId", th.IntegerType),
        th.Property("TicketTypeId", th.IntegerType),
        th.Property("SubscriptionTypeId", th.IntegerType),
        th.Property("TicketType", th.StringType),
        th.Property("PriceZoneId", th.IntegerType),
        th.Property("PriceZone", th.IntegerType),
        th.Property("Section", th.StringType),
        th.Property("Row", th.StringType),
        th.Property("Seat", th.StringType),
        th.Property("Entrance", th.StringType),
        th.Property("TicketCount", th.IntegerType),
        th.Property("Price", th.NumberType),
        th.Property("Fee", th.NumberType),
        th.Property("Online", th.BooleanType),
        th.Property("Scanned", th.BooleanType),
        th.Property("SkinID", th.IntegerType),
        th.Property("OrganisationID", th.IntegerType),
        th.Property("Created", th.DateTimeType),
    ).to_dict()