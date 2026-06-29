import re

def parse_description(description: str) -> dict:
    data = {}

    if not description:
        return data

    key_map = {
        "min_age": "min_age",
        "max_age": "max_age",
        "price": "price",
        "instructor": "instructor",
        "category": "category",
        "description": "description",
    }

    lines = description.splitlines()

    for line in lines:
        if ":" not in line:
            continue

        raw_key, _, value = line.partition(":")
        key = raw_key.strip().lower()
        # נקי תווים בלתי נראים
        value = re.sub(r'[\u200e\u200f\xa0]', ' ', value).strip()

        if key in key_map:
            data[key_map[key]] = value
    return data
