import philip_snat_models.khl.urls as urls
import datetime

today = datetime.datetime.now().strftime("%d.%m.%Y")


def is_date_before(date1, date2):
    if isinstance(date1, str):
        date1 = datetime.datetime.strptime(date1, "%d.%m.%Y")
    if isinstance(date2, str):
        date2 = datetime.datetime.strptime(date2, "%d.%m.%Y")
    return date1 < date2


class clr:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DIM = "\033[2m"


team_stats_column_map = {
    "GpG": 10,
    "PMpG": 14,
    "SpG": 16,
    "SVpG": 19,
    "SV%": 20,
    "PP%": 23,
    "PPGApG": 25,
    "PK%": 26,
}

team_names_map = {
    "Shanghai Dragons": {
        "quant": "Shanghai Dragons",
        "sportbox": "Шанхайские Драконы",
        "sportbox_url_name": "Krasnaja_zvezda_Kunlun_Pekin_Khokkej",
        "url_template": urls.TEAM_LAST_GAMES1,
    },
    "Lada Togliatti": {
        "quant": "Lada Togliatti",
        "sportbox": "Лада",
        "sportbox_url_name": "Lada-Toliyatti-Hokkey",
        "url_template": urls.TEAM_LAST_GAMES1,
    },
    "Sibir Novosibirsk": {
        "quant": "Sibir Novosibirsk",
        "sportbox": "Сибирь",
        "sportbox_url_name": "sibir",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Salavat Yulaev Ufa": {
        "quant": "Salavat Yulaev Ufa",
        "sportbox": "Салават Юлаев",
        "sportbox_url_name": "salavat",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Amur Khabarovsk": {
        "quant": "Amur Khabarovsk",
        "sportbox": "Амур",
        "sportbox_url_name": "amur",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "HK Sochi": {
        "quant": "HK Sochi",
        "sportbox": "ХК Сочи",
        "sportbox_url_name": "Sochinskie-leopardi-Sochi-Hokkey",
        "url_template": urls.TEAM_LAST_GAMES1,
    },
    "Admiral Vladivostok": {
        "quant": "Admiral Vladivostok",
        "sportbox": "Адмирал",
        "sportbox_url_name": "Admiral-Vladivostok-Hokkey",
        "url_template": urls.TEAM_LAST_GAMES1,
    },
    "Dynamo Moscow": {
        "quant": "Dynamo Moscow",
        "sportbox": "Динамо",
        "sportbox-dynamo": "Динамо Москва",
        "sportbox_url_name": "dynamo-moscow",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Ak Bars Kazan": {
        "quant": "Ak Bars Kazan",
        "sportbox": "Ак Барс",
        "sportbox_url_name": "ak-bars",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Severstal Cherepovets": {
        "quant": "Severstal Cherepovets",
        "sportbox": "Северсталь",
        "sportbox_url_name": "severstal",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Barys Nur-Sultan": {
        "quant": "Barys Nur-Sultan",
        "sportbox": "Барыс",
        "sportbox_url_name": "barys",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Dinamo Minsk": {
        "quant": "Dinamo Minsk",
        "sportbox": "Динамо",
        "sportbox-dynamo": "Динамо Минск",
        "sportbox_url_name": "dynamo-minsk",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Avtomobilist Yekaterinburg": {
        "quant": "Avtomobilist Yekaterinburg",
        "sportbox": "Автомобилист",
        "sportbox_url_name": "avto",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Torpedo Nizhny Novgorod": {
        "quant": "Torpedo Nizhny Novgorod",
        "sportbox": "Торпедо",
        "sportbox_url_name": "torpedo-nn",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Traktor Chelyabinsk": {
        "quant": "Traktor Chelyabinsk",
        "sportbox": "Трактор",
        "sportbox_url_name": "traktor",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Spartak Moscow": {
        "quant": "Spartak Moscow",
        "sportbox": "Спартак",
        "sportbox_url_name": "spartak-moscow",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Neftekhimik Nizhnekamsk": {
        "quant": "Neftekhimik Nizhnekamsk",
        "sportbox": "Нефтехимик",
        "sportbox_url_name": "neftekhimik",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "SKA Saint Petersburg": {
        "quant": "SKA Saint Petersburg",
        "sportbox": "CKA",
        "sportbox_url_name": "ska",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Lokomotiv Yaroslavl": {
        "quant": "Lokomotiv Yaroslavl",
        "sportbox": "Локомотив",
        "sportbox_url_name": "lokomotiv",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "CSKA Moscow": {
        "quant": "CSKA Moscow",
        "sportbox": "ЦСКА",
        "sportbox_url_name": "cska",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Avangard Omsk": {
        "quant": "Avangard Omsk",
        "sportbox": "Авангард",
        "sportbox_url_name": "avangard",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
    "Metallurg Magnitogorsk": {
        "quant": "Metallurg Magnitogorsk",
        "sportbox": "Металлург",
        "sportbox_url_name": "metallurg-mg",
        "url_template": urls.TEAM_LAST_GAMES2,
    },
}

team_sportbox_russian_name_map = {
    "Шанхайские Драконы": "Shanghai Dragons",
    "Драконы": "Shanghai Dragons",
    "Лада": "Lada Togliatti",
    "Сибирь": "Sibir Novosibirsk",
    "Салават Юлаев": "Salavat Yulaev Ufa",
    "Амур": "Amur Khabarovsk",
    "ХК Сочи": "HK Sochi",
    "Сочи": "HK Sochi",
    "Адмирал": "Admiral Vladivostok",
    "Динамо Москва": "Dynamo Moscow",
    "Динамо М": "Dynamo Moscow",
    "Ак Барс": "Ak Bars Kazan",
    "Северсталь": "Severstal Cherepovets",
    "Барыс": "Barys Nur-Sultan",
    "Динамо Минск": "Dinamo Minsk",
    "Динамо Мн": "Dinamo Minsk",
    "Автомобилист": "Avtomobilist Yekaterinburg",
    "Торпедо": "Torpedo Nizhny Novgorod",
    "Трактор": "Traktor Chelyabinsk",
    "Спартак": "Spartak Moscow",
    "Нефтехимик": "Neftekhimik Nizhnekamsk",
    "СКА": "SKA Saint Petersburg",
    "Локомотив": "Lokomotiv Yaroslavl",
    "ЦСКА": "CSKA Moscow",
    "Авангард": "Avangard Omsk",
    "Металлург": "Metallurg Magnitogorsk",
}
