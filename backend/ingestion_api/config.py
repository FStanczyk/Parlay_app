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

    DEFAULT_LANG: str = "pl-PL"
    DEFAULT_TARGET: str = "SB_PL"
    DEFAULT_INCLUDE_ONLY: str = "fixture,inPlayStats,inPlayStatsMetadata,results"

    BETBUILDER_GET_MARKETS_ENDPOINT: str = "getBetbuilderMarketsForMatch"
    EVENTS_ENDPOINT: str = "events"

    @property
    def betbuilder_get_markets_url(self) -> str:
        return f"{self.BETBUILDER_BASE_URL}/{self.BETBUILDER_GET_MARKETS_ENDPOINT}"

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
