from rest_framework import serializers
from django.conf import settings
from advocate.connection import (
    validating_create_connection,
    UnacceptableAddressException,
)
from advocate.addrvalidator import AddrValidator
from urllib.parse import urlparse


def validate_events_data(data):
    """
    This function makes sure that if there is the key 'include_all_events' present in a
    dictionary and it is 'False' there needs to be an events dictionary also present.
    Raises DRF ValidationError it the events dictionary is not present.
    """

    data_dict = dict(data)
    data_keys = data.keys()
    include_all_events = data_dict.get("include_all_events", None)

    if include_all_events is None:
        # in this case we will set the default value of 'True'
        # hence no further validation needs to take place
        return data

    if not include_all_events and "events" not in data_keys:
        raise serializers.ValidationError("events must be provided")
    return data


def url_validation(value):
    """
    This is a custom url validation, needed in order to make sure that users will not
    enter a url which could be in the network of where baserow is running.
    It makes use of the advocate libraries own address validation.
    """

    # in case we run the develop server we want to allowe every url.
    if settings.DEBUG is True:
        return value

    url = urlparse(value)

    # in case the user does not provide a port we assume 80 if it is a
    # http url or 443 otherwise.
    if url.port is None:
        if url.scheme == "http":
            port = 80
        else:
            port = 443
    else:
        port = url.port

    addr_validator = AddrValidator()

    try:
        validating_create_connection((url.hostname, port), validator=addr_validator)
        return value
    except UnacceptableAddressException:
        raise serializers.ValidationError(detail="Not a valid url", code="invalid_url")


def http_header_validation(value):
    headers = [x["header"].strip().lower().capitalize() for x in value]

    if len(headers) != len(set(headers)):
        raise serializers.ValidationError(
            detail="Please provide unambigous headers", code="ambigous_headers"
        )

    if "content-type" in headers:
        raise serializers.ValidationError(
            detail="You cannot override content-type", code="wrong_header"
        )

    return value
