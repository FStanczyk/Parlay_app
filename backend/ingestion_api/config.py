from pydantic_settings import BaseSettings
from typing import Optional


class IngestionApiConfig(BaseSettings):
    BETBUILDER_BASE_URL: str = (
        "https://production-superbet-bmb.freetls.fastly.net/betbuilder/v2"
    )
    EVENTS_BASE_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v3/subscription"
    )
    LEAGUE_EVENTS_BASE_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v2/pl-PL/events/by-date?currentStatus=active&offerState=prematch"
    )

    TOURNAMENTS_BASE_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v2/pl-PL/sport/{sport_id}/tournaments"
    )

    STRUCT_BASE_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v2/pl-PL/struct"
    )

    CHECK_EVENTS_BASE_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v2/pl-PL/events/{event_id}"
    )

    SPORT_PREMATCH_MARKETS_URL: str = (
        "https://production-superbet-offer-pl.freetls.fastly.net/v2/pl-PL/sport/{sport_id}/phase/prematch/market-groups"
    )

    DEFAULT_LANG: str = "pl-PL"
    DEFAULT_TARGET: str = "SB_PL"
    DEFAULT_INCLUDE_ONLY: str = "fixture,inPlayStats,inPlayStatsMetadata,results"

    BETBUILDER_GET_MARKETS_ENDPOINT: str = "getBetbuilderMarketsForMatch"
    EVENTS_ENDPOINT: str = "events"

    MARKET_GROUPS_TO_FILTER_OUT: list[str] = [
        "Super Zmiana",
        "Specjalne",
        "Powołania",
        "Superbets",
        "SuperBets",
        "Szybkie",
        "Łączone",
        "Statystyki",
    ]

    MARKET_NAMES_TO_FILTER_OUT: list[str] = [
        "liczba odbiorów",
        "Zawodnik - liczba celnych strzałów",
        "Zawodnik - liczba strzałów",
        "Zawodnik - liczba popełnionych fauli",
        "Zawodnik - otrzyma czerwoną kartkę",
        "Zawodnik - otrzyma kartkę",
        "Zawodnik - strzeli 1. gola",
        "Zawodnik - strzeli gola prawą nogą",
        "Zawodnik - strzeli gola lewą nogą",
        "Zawodnik - strzeli gola głową",
        "Zawodnik - strzeli gola z rzutu karnego",
        "Zawodnik - strzeli gola spoza pola karnego",
        "Multiwynik",
        "Przedział goli w każdej połowie",
        "którakolwiek drużyna zachowa czyste konto",
        "Połowa z największą liczbą goli",
        "Obie drużyny strzelą gola lub",
        "Obie drużyny strzelą gola &",
        "1.połowa liczba goli &",
        "1.Połowa Liczba goli &",
        "otrzyma 1. kartkę",
        "wygra lub",
        "remis lub",
        "Remis lub",
        "Liczba kartek - handicap -",
        "Którykolwiek z zawodników strzeli gola",
        "strzeli 1. gola dla ",
        "Obaj zawodnicy strzelą gola",
        "Zawodnik - Liczba podań",
        "Zawodnik - liczba przechwytów",
        "Zawodnik - strzeli gola w 1. połowie",
        "Zawodnik - strzeli gola w 2. połowie",
        "Zawodnik - strzeli gola w obu połowach",
        "Każda z drużyn powyżej X obronionych strzałów przez bramkarza",
    ]

    @property
    def betbuilder_get_markets_url(self) -> str:
        return f"{self.BETBUILDER_BASE_URL}/{self.BETBUILDER_GET_MARKETS_ENDPOINT}"

    def sport_prematch_markets_url(self, sport_id: int) -> str:
        return self.SPORT_PREMATCH_MARKETS_URL.replace("{sport_id}", str(sport_id))

    @property
    def events_url(self) -> str:
        return f"{self.EVENTS_BASE_URL}/{self.DEFAULT_LANG}/{self.EVENTS_ENDPOINT}"

    @property
    def struct_url(self) -> str:
        return self.STRUCT_BASE_URL

    def league_games_url(
        self, start_date: str, end_date: str, sport_id: int, tournament_ids
    ) -> str:
        if isinstance(tournament_ids, (list, tuple)):
            tournament_ids_str = ",".join(str(tid) for tid in tournament_ids)
        else:
            tournament_ids_str = str(tournament_ids)
        return f"{self.LEAGUE_EVENTS_BASE_URL}&startDate={start_date}+00:00:00&endDate={end_date}+00:00:00&sportId={sport_id}&tournamentIds={tournament_ids_str}"

    def tournaments_url(self, sport_id: int) -> str:
        return self.TOURNAMENTS_BASE_URL.replace("{sport_id}", str(sport_id))

    def check_events_url(self, event_id: int) -> str:
        return self.CHECK_EVENTS_BASE_URL.replace("{event_id}", str(event_id))

    class Config:
        env_file = ".env"
        env_prefix = "INGESTION_API_"


config = IngestionApiConfig()
