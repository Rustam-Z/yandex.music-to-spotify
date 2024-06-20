import re


def clean_string(s):
    """
    Clean a string by converting to lowercase, removing special characters and numbers, and removing extra spaces.
    """
    s = s.strip().replace("\t", " ")
    s = re.sub(r"\s+", " ", s)
    return s
