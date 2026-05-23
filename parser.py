def parse_description(description):
    data = {}
    lines = description.splitlines("\n")

    for line in lines:
        if ":" in line:
            key,value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data
