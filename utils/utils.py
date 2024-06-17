import re


def clean_string(s):
    """
    Clean a string by converting to lowercase, removing special characters and numbers, and removing extra spaces.
    """
    s = s.lower().strip().replace("\n", " ").replace("\t", " ")
    s = re.sub(r"[^a-z\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
