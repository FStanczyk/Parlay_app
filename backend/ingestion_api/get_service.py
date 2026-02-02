#!/usr/bin/env python3

import json
import logging
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion_api.request_handler import req
from ingestion_api.config import config
from datetime import datetime, timedelta
from ingestion_api.helpers import (
    Helpers,
    Game,
    BetEvent,
    Sport as SportData,
    League,
)

logger = logging.getLogger(__name__)


def get_league_games(sport_id: int, tournament_ids, days_forward=3) -> List[Game]:
    today = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_forward)).strftime("%Y-%m-%d")
    url = config.league_games_url(
        start_date=today,
        end_date=end_date,
        sport_id=sport_id,
        tournament_ids=tournament_ids,
    )
    logger.debug(f"Fetching league games: {url}")
    data = req.get_json(url)

    games = []
    for game_data in data.get("data", []):
        match_name = game_data.get("matchName", "")
        home_team, away_team = Helpers.retrieve_team_names(match_name)
        game_datetime = Helpers.retrieve_game_datetime(game_data)
        game = Game(
            datetime=game_datetime,
            sport_id=sport_id,
            league_id=game_data.get("tournamentId"),
            home_team=home_team,
            away_team=away_team,
            odds_api_id=(
                str(game_data.get("eventId")) if game_data.get("eventId") else None
            ),
        )
        games.append(game)

    return games


def get_game_odds_events(game_id: int) -> List[BetEvent]:
    from requests.exceptions import HTTPError

    url = config.betbuilder_get_markets_url
    params = {
        "match_id": str(game_id),
        "lang": config.DEFAULT_LANG,
        "target": config.DEFAULT_TARGET,
    }

    try:
        data = req.get_json(url, params=params)
    except HTTPError as e:
        if e.response and e.response.status_code == 404:
            logger.warning(f"Game {game_id} not found (404) - skipping bet events")
            return []
        logger.warning(
            f"HTTP error retrieving bet events for game {game_id}: {e.response.status_code if e.response else 'unknown'} - skipping"
        )
        return []
    except Exception as e:
        logger.warning(
            f"Error retrieving bet events for game {game_id}: {str(e)} - skipping"
        )
        return []

    if not data:
        return []

    markets = data.get("markets", []) or []
    betEvents = []
    for market in markets:
        if not market:
            continue
        odds = market.get("odds", []) or []
        for odd in odds:
            if not odd:
                continue

            price = odd.get("price")
            if price is None:
                continue

            betEvent = BetEvent(
                odds=float(price),
                event=f"{market.get('name', '')} - {odd.get('name', '')}",
                odds_api_id=odd.get("uuid"),
                game_odds_api_id=str(game_id),
                category_name=market.get("name"),
                category_id=market.get("id"),
            )

            betEvents.append(betEvent)

    return betEvents


def get_tournaments(sport_id: int) -> List[League]:
    url = config.tournaments_url(sport_id=sport_id)
    data = req.get_json(url)
    tournaments_data = data.get("data", [])
    leagues = []

    for tournament_data in tournaments_data:
        local_names = tournament_data.get("localNames", {})
        country_code = local_names.get("pl-PL", "")

        for competition in tournament_data.get("competitions", []):
            competition_id = competition.get("tournamentId")
            competition_name = competition.get("localNames", {}).get("pl-PL", "")

            league = League(
                sport_id=sport_id,
                odds_api_id=str(competition_id),
                name=competition_name,
                country_code=country_code,
                download=False,
            )
            leagues.append(league)

    return leagues


def get_sports_from_struct() -> List[SportData]:
    url = config.struct_url
    res = req.get_json(url)
    data = res.get("data", {})
    sports_data = data.get("sports", [])
    sports = []
    for sport_data in sports_data:
        sport = SportData(
            id=sport_data.get("id"),
            name=sport_data.get("localNames", {}).get("pl-PL", ""),
        )
        sports.append(sport)
    return sports


def get_results_from_event_stream(event_id: int, db=None):
    import json
    from app.core.database import SessionLocal
    from app.models.bet_event import BetEvent, BetResult

    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False

    try:
        url = config.events_url
        params = {"events": str(event_id), "includeOnly": config.DEFAULT_INCLUDE_ONLY}

        response = req.get(url, params=params, stream=True)
        response.raise_for_status()

        first_message = None
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data:"):
                json_str = line[5:].strip()
                try:
                    first_message = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    continue
            elif line.strip() and not line.startswith(":"):
                try:
                    first_message = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue

        if not first_message:
            logger.warning(f"No data received from stream for event {event_id}")
            return None

        data = first_message
        updated_count = 0

        if isinstance(data, list) and len(data) > 0 and "results" in data[0]:
            results = data[0]["results"]

            for result in results:
                market_name = result.get("name", "Unknown")
                odds_list = result.get("odds", [])

                for odd in odds_list:
                    uuid = odd.get("uuid")
                    if not uuid:
                        continue

                    status = odd.get("status")
                    price = odd.get("price")

                    bet_result = None
                    if status == 3 and price == 1:
                        bet_result = BetResult.WIN
                    elif status == 4 and price == 0:
                        bet_result = BetResult.LOOSE
                    elif status == 0:
                        bet_result = BetResult.TO_RESOLVE
                    elif status == 5:
                        bet_result = BetResult.VOID
                    else:
                        bet_result = BetResult.UNKNOWN

                    bet_event = (
                        db.query(BetEvent).filter(BetEvent.odds_api_id == uuid).first()
                    )

                    if bet_event:
                        bet_event.result = bet_result
                        updated_count += 1
                        logger.debug(
                            f"Updated bet_event {uuid}: {bet_result.value} (status: {status}, price: {price})"
                        )
                    else:
                        logger.warning(
                            f"Bet event with UUID {uuid} not found in database"
                        )

        db.commit()
        logger.info(f"Updated {updated_count} bet events for event {event_id}")
        return data

    except Exception as e:
        db.rollback()
        logger.error(
            f"Error processing results for event {event_id}: {str(e)}", exc_info=True
        )
        raise
    finally:
        if should_close:
            db.close()


def is_game_finished(event_id: int) -> bool:
    try:
        url = config.check_events_url(event_id)
        data = req.get_json(url)

        if not data or not data.get("data") or len(data["data"]) == 0:
            return False

        event_data = data["data"][0]
        offer_state_status = event_data.get("offerStateStatus", {})

        state_1 = offer_state_status.get("1", "").lower()
        state_2 = offer_state_status.get("2", "").lower()

        is_finished = state_1 == "finished" and state_2 == "finished"
        logger.debug(
            f"Game {event_id} finished status: {is_finished} (state_1: {state_1}, state_2: {state_2})"
        )
        return is_finished
    except Exception as e:
        logger.error(
            f"Error checking if game {event_id} is finished: {str(e)}", exc_info=True
        )
        return False
