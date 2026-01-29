from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass


class Helpers:
    @staticmethod
    def retrieve_team_names(match_name: str) -> tuple[str, str]:
        home_team = match_name.split("·")[0].strip()
        away_team = match_name.split("·")[1].strip()
        return home_team, away_team

    @staticmethod
    def retrieve_game_datetime(game_data: dict) -> datetime:
        match_date_str = game_data.get("matchDate", "")
        try:
            game_datetime = datetime.strptime(match_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                game_datetime = datetime.fromisoformat(
                    match_date_str.replace("Z", "+00:00")
                )
            except ValueError:
                return None
        return game_datetime


@dataclass
class Game:
    datetime: datetime
    sport_id: int
    league_id: int
    home_team: str
    away_team: str
    odds_api_id: str = None
    status: str = None
    winner: str = None
    home_team_score: int = None
    away_team_score: int = None
    overtime: bool = None
    shootout: bool = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datetime": self.datetime,
            "sport_id": self.sport_id,
            "league_id": self.league_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "odds_api_id": self.odds_api_id,
            "status": self.status,
            "winner": self.winner,
            "home_team_score": self.home_team_score,
            "away_team_score": self.away_team_score,
            "overtime": self.overtime,
            "shootout": self.shootout,
        }


@dataclass
class BetEvent:
    odds: float
    event: str
    game_id: int = None
    result: str = None
    odds_api_id: str = None
    game_odds_api_id: str = None
    category_name: str = None
    category_id: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "odds": self.odds,
            "game_id": self.game_id,
            "event": self.event,
            "result": self.result,
            "odds_api_id": self.odds_api_id,
            "game_odds_api_id": self.game_odds_api_id,
            "category_name": self.category_name,
            "category_id": self.category_id,
        }


@dataclass
class League:
    sport_id: int
    odds_api_id: str
    name: str
    country_code: str = ""
    download: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sport_id": self.sport_id,
            "odds_api_id": self.odds_api_id,
            "name": self.name,
            "country_code": self.country_code,
            "download": self.download,
        }


class Sport:
    id: int
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
        }
