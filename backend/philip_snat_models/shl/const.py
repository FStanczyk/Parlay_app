from datetime import datetime, timedelta

SEASON_UUID = "xs4m9qupsi"
SERIES_UUID = "qQ9-bb0bzEWUk"
GAME_TYPE_UUID = "qQ9-af37Ti40B"
SSGT_UUID = "iuzqg7dqk9"

CODES = [
    "BIF", "FBK", "LHF", "FHC", "OHK", "SAIK", "TIK", "MIF",
    "RBK", "VLH", "LIF", "HV71", "LHC", "MODO", "DIF"
]

UUIDS = [
    "1ab8-1ab8bfj7N", "752c-752c12zB7Z", "1a71-1a71gTHKh", "087a-087aTQv9u",
    "82eb-82ebmgaJ8", "50e6-50e6DYeWM", "31d1-31d1NbSlR", "8e6f-8e6fUXJvi",
    "ee93-ee93uy4oW", "fe02-fe02mf1FN", "9541-95418PpkP", "3db0-3db09jXTE",
    "41c4-41c4BiYZU", "110b-110bJcIAI", "2459-2459QTs1f"
]

CODE_UUID_MAP = {
    "BIF": "1ab8-1ab8bfj7N", "FBK": "752c-752c12zB7Z", "LHF": "1a71-1a71gTHKh",
    "FHC": "087a-087aTQv9u", "OHK": "82eb-82ebmgaJ8", "SAIK": "50e6-50e6DYeWM",
    "TIK": "31d1-31d1NbSlR", "MIF": "8e6f-8e6fUXJvi", "RBK": "ee93-ee93uy4oW",
    "VLH": "fe02-fe02mf1FN", "LIF": "9541-95418PpkP", "HV71": "3db0-3db09jXTE",
    "LHC": "41c4-41c4BiYZU", "MODO": "110b-110bJcIAI", "DIF": "2459-2459QTs1f"
}

UUID_CODE_MAP = {v: k for k, v in CODE_UUID_MAP.items()}

CODE_NAME_MAP = {
    "BIF": "Brynäs IF", "FBK": "Färjestad BK", "LHF": "Luleå Hockey",
    "FHC": "Frölunda HC", "OHK": "Örebro Hockey", "SAIK": "Skellefteå AIK",
    "TIK": "Timrå IK", "MIF": "Malmö Redhawks", "RBK": "Rögle BK",
    "VLH": "Växjö Lakers", "LIF": "Leksands IF", "HV71": "HV71",
    "LHC": "Linköping HC", "MODO": "MoDo Hockey", "DIF": "Djurgårdens IF"
}

NAME_CODE_MAP = {v: k for k, v in CODE_NAME_MAP.items()}

UUID_NAME_MAP = {
    "1ab8-1ab8bfj7N": "Brynäs IF", "752c-752c12zB7Z": "Färjestad BK",
    "1a71-1a71gTHKh": "Luleå Hockey", "087a-087aTQv9u": "Frölunda HC",
    "82eb-82ebmgaJ8": "Örebro Hockey", "50e6-50e6DYeWM": "Skellefteå AIK",
    "31d1-31d1NbSlR": "Timrå IK", "8e6f-8e6fUXJvi": "Malmö Redhawks",
    "ee93-ee93uy4oW": "Rögle BK", "fe02-fe02mf1FN": "Växjö Lakers",
    "9541-95418PpkP": "Leksands IF", "3db0-3db09jXTE": "HV71",
    "41c4-41c4BiYZU": "Linköping HC", "110b-110bJcIAI": "MoDo Hockey",
    "2459-2459QTs1f": "Djurgårdens IF"
}

NAME_UUID_MAP = {v: k for k, v in UUID_NAME_MAP.items()}


def today():
    return datetime.today().strftime("%Y-%m-%d")


def day_before(day):
    yesterday = datetime.strptime(day, "%Y-%m-%d") - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def day_after(day):
    tomorrow = datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


def is_after(date1, date2):
    date1 = date1.split(" ")[0]
    date2 = date2.split(" ")[0]
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return d1 > d2


def is_before(date1, date2):
    date1 = date1.split(" ")[0]
    date2 = date2.split(" ")[0]
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return d1 < d2


def detag(tag, into="code"):
    if into not in {"code", "uuid", "name"}:
        raise ValueError("Invalid 'into' value. Must be one of 'code', 'uuid', or 'name'.")

    if into == "code" and tag in CODES:
        return tag
    elif into == "uuid" and tag in UUIDS:
        return tag
    elif into == "name" and tag in NAME_CODE_MAP:
        return tag

    if into == "code":
        if tag in NAME_CODE_MAP:
            return NAME_CODE_MAP[tag]
        if tag in UUID_CODE_MAP:
            return UUID_CODE_MAP[tag]
    elif into == "uuid":
        if tag in NAME_UUID_MAP:
            return NAME_UUID_MAP[tag]
        if tag in CODE_UUID_MAP:
            return CODE_UUID_MAP[tag]
    elif into == "name":
        if tag in CODE_NAME_MAP:
            return CODE_NAME_MAP[tag]
        if tag in UUID_NAME_MAP:
            return UUID_NAME_MAP[tag]

    return None


def uuid_by_code(code):
    return CODE_UUID_MAP.get(code)


def code_by_uuid(uuid):
    return UUID_CODE_MAP.get(uuid)


def name_by_code(code):
    return CODE_NAME_MAP.get(code)


def code_by_name(name):
    return NAME_CODE_MAP.get(name)


def get_from_array_by_value(array, by_name, by_value, field_name_to_get):
    for a in array:
        if a.get(by_name) == by_value:
            return a.get(field_name_to_get)
    return None


def get_from_array_by_value2(array, by_name, by_value, field_name_to_get):
    for a in array:
        if a.get("info", {}).get(by_name) == by_value:
            return a.get(field_name_to_get)
    return None
