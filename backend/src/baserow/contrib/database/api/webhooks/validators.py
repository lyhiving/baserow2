from rest_framework import serializers


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
    # sess = Session()

    # try:
    #    sess.get(value)
    # except UnacceptableAddressException:
    #    raise serializers.ValidationError(detail="Not a valid url", code="invalid_url")

    return value


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
