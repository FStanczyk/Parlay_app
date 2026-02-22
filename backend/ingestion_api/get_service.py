#!/usr/bin/env python3

import json
import logging
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.bet_event import BetResult, BetEvent
from app.models.bet_recommendation import BetRecommendation
from app.models.tipster_ranges import TipsterRange
from app.models.tipster_main_stats import TipsterMainStats
from app.models.tipster_tier_stats import TipsterTierStats
from app.models.tipster_main_range_stats import TipsterMainRangeStats
from app.models.tipster_tiers_range_stats import TipsterTiersRangeStats
from ingestion_api.request_handler import req
from ingestion_api.config import config
from datetime import datetime, timedelta
from ingestion_api.helpers import (
    Helpers,
    Game,
    BetEvent as BetEventHelper,
    Sport as SportData,
    League,
)
from app.core.database import SessionLocal

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

    url = config.check_events_url(game_id)

    try:
        data = req.get_json(url)
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

    _data = data.get("data", []) or []
    if not _data:
        return []

    event = _data[0]
    odds = event.get("odds", []) or []

    market_url = config.sport_prematch_markets_url(sport_id=event.get("sportId"))
    market_data = req.get_json(market_url)
    betEvents = []
    logger.info(f"Processing results for game {game_id}")
    for odd in odds:

        if filter_out_market_groups(market_data, odd.get("marketId")):
            continue

        if filter_out_market_names(odd.get("marketName")):
            continue

        betEvent = BetEvent(
            odds=float(odd.get("price")),
            event=f"{odd.get('marketName', '')} - {odd.get('name', '')}",
            odds_api_id=odd.get("uuid"),
            category_name=odd.get("marketName"),
            category_id=odd.get("marketId"),
        )
        betEvents.append(betEvent)

    return betEvents


def find_market_group_of_bet(market_data: dict, market_id) -> dict:
    if not market_data:
        return None
    for market_group in market_data.get("data", []) or []:
        markets = market_group.get("markets") or []
        if market_id in markets:
            return market_group
    return None


def filter_out_market_names(market_name: str) -> bool:
    if not market_name:
        return False
    return any(name in market_name for name in config.MARKET_NAMES_TO_FILTER_OUT)


def filter_out_market_groups(market_data: dict, market_id) -> bool:
    market_group = find_market_group_of_bet(market_data, market_id)
    if (
        market_group
        and market_group.get("localNames", {}).get("pl-PL", "")
        in config.MARKET_GROUPS_TO_FILTER_OUT
    ):
        return True
    return False


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
                        if bet_event.result != bet_result:
                            bet_event.result = bet_result
                            updated_count += 1
                            logger.debug(
                                f"Updated bet_event {uuid}: {bet_result.value} (status: {status}, price: {price})"
                            )

                            update_tipster_stats(bet_event, bet_result, db)
                        else:
                            logger.debug(
                                f"Bet event {uuid} already has result {bet_result.value}, skipping"
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


def update_tipster_stats(bet_event: BetEvent, bet_result: BetResult, db):
    if bet_result is None or bet_result not in [BetResult.WIN, BetResult.LOOSE]:
        return

    recommendations = (
        db.query(BetRecommendation)
        .filter(BetRecommendation.bet_event_id == bet_event.id)
        .all()
    )

    for recommendation in recommendations:
        rec_tipster_id = recommendation.tipster_id
        rec_odds = recommendation.bet_event.odds
        rec_stake = recommendation.stake if recommendation.stake else 1.0
        rec_tier_id = recommendation.tipster_tier_id
        rec_has_description = (
            recommendation.tipster_description is not None
            and recommendation.tipster_description.strip() != ""
        )

        rec_won = bet_result == BetResult.WIN
        rec_return = rec_stake * rec_odds if rec_won else 0.0

        main_stats = (
            db.query(TipsterMainStats)
            .filter(TipsterMainStats.tipster_id == rec_tipster_id)
            .first()
        )

        if not main_stats:
            main_stats = TipsterMainStats(
                tipster_id=rec_tipster_id,
                total_picks=0,
                total_return=0,
                total_picks_won=0,
                sum_odds=0,
                sum_stake=0.0,
                picks_with_description=0,
            )
            db.add(main_stats)

        main_stats.total_picks += 1
        main_stats.total_picks_won += 1 if rec_won else 0
        main_stats.sum_stake += rec_stake
        main_stats.total_return += rec_return
        main_stats.sum_odds += rec_odds
        main_stats.picks_with_description += 1 if rec_has_description else 0

        if rec_tier_id:
            tier_stats = (
                db.query(TipsterTierStats)
                .filter(TipsterTierStats.tipster_tier_id == rec_tier_id)
                .first()
            )

            if not tier_stats:
                tier_stats = TipsterTierStats(
                    tipster_id=rec_tipster_id,
                    tipster_tier_id=rec_tier_id,
                    total_picks=0,
                    total_return=0,
                    total_picks_won=0,
                    sum_odds=0,
                    sum_stake=0.0,
                    picks_with_description=0,
                )
                db.add(tier_stats)

            tier_stats.total_picks += 1
            tier_stats.total_picks_won += 1 if rec_won else 0
            tier_stats.sum_stake += rec_stake
            tier_stats.total_return += rec_return
            tier_stats.sum_odds += rec_odds
            tier_stats.picks_with_description += 1 if rec_has_description else 0

        odds_range = (
            db.query(TipsterRange)
            .filter(
                TipsterRange.range_start <= rec_odds,
                TipsterRange.range_end >= rec_odds,
            )
            .first()
        )

        if odds_range:
            main_range_stats = (
                db.query(TipsterMainRangeStats)
                .filter(
                    TipsterMainRangeStats.tipster_id == rec_tipster_id,
                    TipsterMainRangeStats.range_id == odds_range.id,
                )
                .first()
            )

            if not main_range_stats:
                main_range_stats = TipsterMainRangeStats(
                    tipster_id=rec_tipster_id,
                    range_id=odds_range.id,
                    total_picks=0,
                    total_return=0,
                    total_picks_won=0,
                    sum_stake=0.0,
                )
                db.add(main_range_stats)

            main_range_stats.total_picks += 1
            main_range_stats.total_picks_won += 1 if rec_won else 0
            main_range_stats.sum_stake += rec_stake
            main_range_stats.total_return += rec_return

            if rec_tier_id:
                tier_range_stats = (
                    db.query(TipsterTiersRangeStats)
                    .filter(
                        TipsterTiersRangeStats.tipster_tier_id == rec_tier_id,
                        TipsterTiersRangeStats.range_id == odds_range.id,
                    )
                    .first()
                )

                if not tier_range_stats:
                    tier_range_stats = TipsterTiersRangeStats(
                        tipster_id=rec_tipster_id,
                        tipster_tier_id=rec_tier_id,
                        range_id=odds_range.id,
                        total_picks=0,
                        total_return=0,
                        total_picks_won=0,
                        sum_stake=0.0,
                    )
                    db.add(tier_range_stats)

                tier_range_stats.total_picks += 1
                tier_range_stats.total_picks_won += 1 if rec_won else 0
                tier_range_stats.sum_stake += rec_stake
                tier_range_stats.total_return += rec_return

        db.commit()
        logger.info(
            f"Updated stats for tipster {rec_tipster_id}, recommendation {recommendation.id}"
        )


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


def debug_check_market_groups(game_id: int):
    url = config.check_events_url(game_id)
    data = req.get_json(url)

    if not data:
        print(f"No data for game {game_id}")
        return

    _data = data.get("data", []) or []
    if not _data:
        print(f"Empty data for game {game_id}")
        return

    event = _data[0]
    odds = event.get("odds", []) or []

    market_url = config.sport_prematch_markets_url(sport_id=event.get("sportId"))
    market_data = req.get_json(market_url)

    entries = []
    for odd in odds:
        event_label = f"{odd.get('marketName', '')} - {odd.get('name', '')}"
        market_group = find_market_group_of_bet(market_data, odd.get("marketId"))
        group_name = (
            market_group.get("localNames", {}).get("pl-PL", "N/A")
            if market_group
            else "N/A"
        )
        entries.append({"event": event_label, "group": group_name})

    import os

    os.makedirs("/app/temp", exist_ok=True)
    out_path = f"/app/temp/log_markets_{game_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(entries)} entries to {out_path}")
