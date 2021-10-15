from rest_framework import serializers


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
