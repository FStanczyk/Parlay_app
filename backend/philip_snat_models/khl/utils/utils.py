from philip_snat_models.khl.const import today
import datetime


def safe_float_conversion(value, default=0.0):
    if not value or value == "":
        return default
    try:
        return float(str(value).replace("%", ""))
    except ValueError:
        return default


def check_if_date_is_valid(upcoming_game, for_tomorrow=False):
    first_td = upcoming_game.find("td")
    date_span = first_td.find("span")
    game_date_str = date_span.get_text().strip()
    game_date = game_date_str.split("&")[0].strip()[:5]
    today_date = today.split(".")[:2]
    tomorrow_date = (
        datetime.datetime.strptime(today, "%d.%m.%Y") + datetime.timedelta(days=1)
    ).strftime("%d.%m.%Y")
    tomorrow_date = tomorrow_date.split(".")[:2]
    tomorrow_str = f"{tomorrow_date[0]}.{tomorrow_date[1]}"
    today_str = f"{today_date[0]}.{today_date[1]}"
    if for_tomorrow:
        return game_date == tomorrow_str
    else:
        return game_date == today_str


def check_if_should_skip_game(upcoming_game, for_tomorrow):
    if for_tomorrow:
        first_td = upcoming_game.find("td")
        date_span = first_td.find("span")
        game_date_str = date_span.get_text().strip()
        game_date = game_date_str.split("&")[0].strip()[:5]
        tomorrow_date = (
            datetime.datetime.strptime(today, "%d.%m.%Y") + datetime.timedelta(days=1)
        ).strftime("%d.%m.%Y")
        tomorrow_date = tomorrow_date.split(".")[:2]
        tomorrow_str = f"{tomorrow_date[0]}.{tomorrow_date[1]}"

        game_datetime = datetime.datetime.strptime(f"{game_date}.2025", "%d.%m.%Y")
        tomorrow_datetime = datetime.datetime.strptime(f"{tomorrow_str}.2025", "%d.%m.%Y")
        return game_datetime < tomorrow_datetime
    else:
        return False
