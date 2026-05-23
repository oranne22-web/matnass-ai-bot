def parse_description(description):
    data = {}

    if not description:
        return data

    lines = description.splitlines()

    for line in lines:
        if ":" in line:
            key,value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data
