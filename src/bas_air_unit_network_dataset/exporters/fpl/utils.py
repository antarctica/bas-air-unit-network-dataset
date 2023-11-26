import re


def _upper_alphanumeric_space_only(value: str) -> str:
    """
    Strip non upper-case alphanumeric or space (' ') characters from string.

    E.g. 'FOO bar 12' would become 'FOO  12' (double space as we don't post-process values).

    :type value: str
    :param value: string to process
    :return: processed string
    """
    return re.sub(r"[^A-Z\d ]+", "", value)


def _upper_alphanumeric_only(value: str) -> str:
    """
    Strip non upper-case alphanumeric characters from string.

    E.g. 'FOO bar 12' would become 'FOO12'.

    :type value: str
    :param value: string to process
    :return: processed string
    """
    return re.sub(r"[^A-Z\d]+", "", value)
