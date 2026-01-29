#!/usr/bin/env python3

import datetime
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion_api.get_service import (
    get_results_from_event_stream,
    get_sports_from_struct,
    get_league_games,
    get_game_odds_events,
    is_game_finished,
)
from ingestion_api.config import config
from ingestion_api.request_handler import req
from app.core.database import SessionLocal
from app.models.sport import Sport
from app.models.league import League
from app.models.game import Game
from app.models.bet_event import BetEvent

logger = logging.getLogger(__name__)

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def populate_sports_to_database():
    db = SessionLocal()
    try:
        sports_data = get_sports_from_struct()
        added_count = 0
        updated_count = 0

        for sport in sports_data:
            existing_sport = (
                db.query(Sport).filter(Sport.odds_api_id == str(sport.id)).first()
            )

            if existing_sport:
                existing_sport.name = sport.name
                updated_count += 1
            else:
                new_sport = Sport(
                    name=sport.name,
                    odds_api_id=str(sport.id),
                )
                db.add(new_sport)
                added_count += 1

        db.commit()
        logger.info(
            f"Successfully populated sports: {added_count} added, {updated_count} updated"
        )
        return {"added": added_count, "updated": updated_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error populating sports: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def get_tournaments_for_sport(sport_id: int):
    url = config.tournaments_url(sport_id=sport_id)
    data = req.get_json(url)
    tournaments_data = data.get("data", [])
    leagues = []

    for tournament_data in tournaments_data:
        local_names = tournament_data.get("localNames", {})
        country_code = local_names.get("pl-PL", "")
        competitions = tournament_data.get("competitions", [])

        if competitions:
            for competition in competitions:
                tournamentId = competition.get("tournamentId")
                competition_name = competition.get("localNames", {}).get(
                    "pl-PL", country_code
                )
                leagues.append(
                    {
                        "name": competition_name,
                        "sport_id": sport_id,
                        "odds_api_id": tournamentId,
                        "country_code": country_code,
                    }
                )

    return leagues


def populate_leagues():
    db = SessionLocal()
    try:
        sports = db.query(Sport).all()
        total_added = 0
        total_updated = 0

        for sport in sports:
            if not sport.odds_api_id:
                logger.warning(
                    f"Skipping sport {sport.name} (ID: {sport.id}) - no odds_api_id"
                )
                continue

            logger.info(
                f"Fetching tournaments for sport: {sport.name} (odds_api_id: {sport.odds_api_id})"
            )
            tournaments = get_tournaments_for_sport(int(sport.odds_api_id))

            for tournament in tournaments:
                tournament_id = str(tournament.get("odds_api_id"))
                tournament_name = tournament.get("name", "")
                tournament_country_code = tournament.get("country_code", "")

                existing_league = (
                    db.query(League).filter(League.odds_api_id == tournament_id).first()
                )

                if existing_league:
                    existing_league.name = tournament_name
                    existing_league.sport_id = sport.id
                    existing_league.country_code = tournament_country_code
                    total_updated += 1
                else:
                    new_league = League(
                        sport_id=sport.id,
                        odds_api_id=tournament_id,
                        name=tournament_name,
                        country_code=tournament_country_code,
                        download=False,
                    )
                    db.add(new_league)
                    total_added += 1

            db.commit()
            logger.info(f"Processed {len(tournaments)} tournaments for {sport.name}")

        logger.info(
            f"Successfully populated leagues: {total_added} added, {total_updated} updated"
        )
        return {"added": total_added, "updated": total_updated}
    except Exception as e:
        db.rollback()
        logger.error(f"Error populating leagues: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def _group_leagues_by_sport(leagues):
    leagues_by_sport = {}
    for league in leagues:
        if not league.odds_api_id or league.odds_api_id == "None":
            continue
        if not league.sport.odds_api_id:
            continue

        try:
            sport_odds_api_id = int(league.sport.odds_api_id)
            tournament_id = int(league.odds_api_id)
        except (ValueError, TypeError):
            continue

        if sport_odds_api_id not in leagues_by_sport:
            leagues_by_sport[sport_odds_api_id] = []
        leagues_by_sport[sport_odds_api_id].append(tournament_id)

    return leagues_by_sport


def _create_batches(tournament_ids, batch_size=10):
    batches = []
    for i in range(0, len(tournament_ids), batch_size):
        batches.append(tournament_ids[i : i + batch_size])
    return batches


def _save_game_to_db(db, api_game, sport, league):
    existing_game = (
        db.query(Game).filter(Game.odds_api_id == api_game.odds_api_id).first()
    )

    if existing_game:
        existing_game.datetime = api_game.datetime
        existing_game.sport_id = sport.id
        existing_game.league_id = league.id
        existing_game.home_team = api_game.home_team
        existing_game.away_team = api_game.away_team
        db_game = existing_game
        is_new = False
    else:
        db_game = Game(
            datetime=api_game.datetime,
            sport_id=sport.id,
            league_id=league.id,
            home_team=api_game.home_team,
            away_team=api_game.away_team,
            odds_api_id=api_game.odds_api_id,
        )
        db.add(db_game)
        is_new = True

    db.flush()
    return db_game, is_new


def _save_bet_events_for_game(db, db_game, api_game_odds_api_id):
    bet_events_added = 0
    try:
        bet_events = get_game_odds_events(int(api_game_odds_api_id))
        logger.debug(
            f"Retrieved {len(bet_events)} bet events for game {api_game_odds_api_id}"
        )

        for bet_event in bet_events:
            existing_bet_event = (
                db.query(BetEvent)
                .filter(BetEvent.odds_api_id == bet_event.odds_api_id)
                .first()
            )

            if not existing_bet_event:
                db_bet_event = BetEvent(
                    odds=bet_event.odds,
                    game_id=db_game.id,
                    event=bet_event.event,
                    odds_api_id=bet_event.odds_api_id,
                    category_name=bet_event.category_name,
                    category_id=bet_event.category_id,
                )
                db.add(db_bet_event)
                bet_events_added += 1
    except Exception as e:
        logger.error(
            f"Error retrieving bet events for game {api_game_odds_api_id}: {str(e)}",
            exc_info=True,
        )

    return bet_events_added


def _process_batch(db, sport, sport_odds_api_id, batch):
    games_added = 0
    games_updated = 0
    bet_events_added = 0

    try:
        api_games = get_league_games(sport_odds_api_id, batch, days_forward=3)
        logger.debug(f"Retrieved {len(api_games)} games from batch")

        for api_game in api_games:
            if not api_game.datetime:
                continue

            league = (
                db.query(League)
                .filter(League.odds_api_id == str(api_game.league_id))
                .first()
            )

            if not league:
                logger.warning(f"Skipping game - league {api_game.league_id} not found")
                continue

            db_game, is_new = _save_game_to_db(db, api_game, sport, league)
            if is_new:
                games_added += 1
            else:
                games_updated += 1

            if api_game.odds_api_id:
                bet_events_added += _save_bet_events_for_game(
                    db, db_game, api_game.odds_api_id
                )

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing batch: {str(e)}", exc_info=True)
        raise

    return games_added, games_updated, bet_events_added


def populate_events():
    db = SessionLocal()
    try:
        leagues = (
            db.query(League)
            .join(Sport, League.sport_id == Sport.id)
            .filter(League.download == True)
            .all()
        )
        leagues = leagues[5:8]
        logger.info(f"Fetched {len(leagues)} league records with download=True")

        leagues_by_sport = _group_leagues_by_sport(leagues)

        if not leagues_by_sport:
            logger.warning("No leagues found for processing")
            return

        games_added = 0
        games_updated = 0
        bet_events_added = 0

        for sport_odds_api_id, tournament_ids in leagues_by_sport.items():
            sport = (
                db.query(Sport)
                .filter(Sport.odds_api_id == str(sport_odds_api_id))
                .first()
            )
            if not sport:
                logger.warning(
                    f"Skipping sport {sport_odds_api_id} - not found in database"
                )
                continue

            batches = _create_batches(tournament_ids)
            logger.info(
                f"Processing sport {sport.name} ({sport_odds_api_id}): {len(tournament_ids)} tournaments in {len(batches)} batches"
            )

            for batch in batches:
                batch_added, batch_updated, batch_bet_events = _process_batch(
                    db, sport, sport_odds_api_id, batch
                )
                games_added += batch_added
                games_updated += batch_updated
                bet_events_added += batch_bet_events

        logger.info("Summary:")
        logger.info(f"  Games added: {games_added}")
        logger.info(f"  Games updated: {games_updated}")
        logger.info(f"  Bet events added: {bet_events_added}")
    except Exception as e:
        logger.error(f"Error fetching leagues: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def clean_old_games():
    db = SessionLocal()
    try:
        deleted_count = (
            db.query(Game)
            .filter(
                Game.datetime < datetime.datetime.now() - datetime.timedelta(days=3)
            )
            .delete()
        )
        db.commit()
        logger.info(f"Cleaned {deleted_count} old games (older than 3 days)")
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning old games: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def set_results_for_event(event_id: int):
    db = SessionLocal()
    try:
        logger.info(f"Setting results for event {event_id}")
        results = get_results_from_event_stream(event_id)
        logger.info(f"Successfully set results for event {event_id}")
    except Exception as e:
        logger.error(
            f"Error setting results for event {event_id}: {str(e)}", exc_info=True
        )
        raise
    finally:
        db.close()


def set_results():
    db = SessionLocal()
    try:
        current_time = datetime.datetime.now()
        games = (
            db.query(Game)
            .filter(Game.datetime < current_time)
            .filter(Game.odds_api_id.isnot(None))
            .all()
        )

        logger.info(f"Found {len(games)} games that have started")

        processed_count = 0
        error_count = 0
        skipped_count = 0

        for game in games:
            if not game.odds_api_id:
                continue

            try:
                event_id = int(game.odds_api_id)

                if not is_game_finished(event_id):
                    logger.debug(
                        f"Game {game.id} (event_id: {event_id}) is not finished yet, skipping"
                    )
                    skipped_count += 1
                    continue

                logger.info(
                    f"Processing results for game {game.id} (event_id: {event_id})"
                )
                get_results_from_event_stream(event_id, db=db)
                processed_count += 1
            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing game {game.id} (event_id: {game.odds_api_id}): {str(e)}",
                    exc_info=True,
                )
                continue

        logger.info("Summary:")
        logger.info(f"  Games processed: {processed_count}")
        logger.info(f"  Games skipped (not finished): {skipped_count}")
        logger.info(f"  Errors: {error_count}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error setting results: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # populate_sports_to_database()
    # populate_events()
    set_results()
    clean_old_games()
