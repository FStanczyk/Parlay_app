from app.models.bet_event import BetEvent
from app.models.game import Game
import httpx
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.sport import Sport
from app.models.league import League
from app.core.config import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OddsDataService:

    def __init__(self):
        self.base_url = getattr(
            settings, "ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4"
        )
        self.api_key = getattr(settings, "ODDS_API_KEY", "")
        self.timeout = 30.0

    async def test(self):
        try:
            logger.info("Starting test - populating sports and leagues...")
            # First, populate sports and leagues if they don't exist
            await self.populate_sports_and_leagues()

            logger.info("Starting test - downloading events and odds...")
            # Then download events and odds for one league
            await self.download_events_and_odds(only_one=True)

            logger.info("Test completed successfully!")
            return "Test completed successfully - check database for bet events"

        except Exception as e:
            logger.error(f"Test error: {str(e)}")
            return None

    async def get_leagues(self):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/sports/"
                params = {
                    "apiKey": self.api_key,
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    async def populate_sports_and_leagues(self):
        db = SessionLocal()
        try:
            leagues = await self.get_leagues()
            unique_groups = set()
            for item in leagues:
                unique_groups.add(item["group"])

            sport_mapping = {}
            for group_name in unique_groups:
                existing_sport = (
                    db.query(Sport).filter(Sport.name == group_name).first()
                )
                if existing_sport:
                    sport_mapping[group_name] = existing_sport.id
                else:
                    new_sport = Sport(name=group_name)
                    db.add(new_sport)
                    db.flush()
                    sport_mapping[group_name] = new_sport.id

            for item in leagues:
                existing_league = (
                    db.query(League)
                    .filter(League.api_league_key == item["key"])
                    .first()
                )

                if not existing_league:
                    new_league = League(
                        sport_id=sport_mapping[item["group"]],
                        api_league_key=item["key"],
                        name=item["title"],
                        country_code="",
                        download=False,  # Default to False
                    )
                    db.add(new_league)

            db.commit()
            logger.info("Successfully populated Sports and Leagues tables")

        except Exception as e:
            db.rollback()
            logger.error(f"Error populating Sports and Leagues: {str(e)}")
            raise
        finally:
            db.close()

    async def download_events_and_odds(self, only_one=False, only_one_by_key=None):
        db = SessionLocal()
        try:
            leagues = db.query(League).filter(League.download == True).all()
            if only_one_by_key:
                leagues = [
                    league
                    for league in leagues
                    if league.api_league_key == only_one_by_key
                ]

            if only_one:
                leagues = [leagues[0]]

            for league in leagues:
                await self.download_events_and_odds_for_league(league)
        except Exception as e:
            db.rollback()
            logger.error(f"Error downloading events and odds: {str(e)}")
            raise
        finally:
            db.close()

    async def download_events_and_odds_for_league(self, league):
        db = SessionLocal()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/sports/{league.api_league_key}/odds/"
                params = {
                    "apiKey": self.api_key,
                    "regions": "eu",
                    "markets": "h2h,totals",
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                for item in data:
                    await self.add_game_events_odds(item, league)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    async def add_game_events_odds(self, game, league):
        db = SessionLocal()
        try:
            home_team = game["home_team"]
            away_team = game["away_team"]
            # Parse the datetime string from the API
            datetime_str = game["commence_time"]
            game_datetime = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

            new_game = await self.add_game(
                home_team, away_team, game_datetime, league.sport_id, league.id
            )

            bookmakers = game["bookmakers"]
            logger.info(
                f"Available bookmakers for {home_team} vs {away_team}: {[b['key'] for b in bookmakers]}"
            )

            # Collect all unique betting opportunities from all bookmakers
            unique_bets = set()

            for bookmaker in bookmakers:
                bookmaker_name = bookmaker["key"]
                logger.info(
                    f"Processing bookmaker {bookmaker_name} for {home_team} vs {away_team}"
                )

                for market in bookmaker["markets"]:
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            odds = outcome["price"]
                            if outcome["name"] == home_team:
                                event_name = "1"
                            elif outcome["name"] == away_team:
                                event_name = "2"
                            else:
                                event_name = "X"

                            bet_key = f"{event_name}|{home_team}|{away_team}|"
                            if bet_key not in unique_bets:
                                unique_bets.add(bet_key)
                                await self.add_odd(
                                    event_name,
                                    odds,
                                    new_game.id,
                                )

                    elif market["key"] == "totals":
                        for outcome in market["outcomes"]:
                            odds = outcome["price"]
                            over_line = outcome["point"]
                            if outcome["name"] == "Over":
                                event_name = f"over {over_line}"
                            elif outcome["name"] == "Under":
                                event_name = f"under {over_line}"
                            else:
                                continue

                            # Create unique identifier for this bet
                            bet_key = f"{event_name}|{home_team}|{away_team}|"
                            if bet_key not in unique_bets:
                                unique_bets.add(bet_key)
                                await self.add_odd(
                                    event_name,
                                    odds,
                                    new_game.id,
                                )

        except Exception as e:
            db.rollback()
            logger.error(f"Error adding game events odds: {str(e)}")
            raise
        finally:
            db.close()

    async def add_odd(self, event_name, odds, game_id):
        if event_name is None or odds is None:
            logger.warning(
                f"Skipping bet event due to missing data: event_name={event_name}, odds={odds}"
            )
            return

        logger.info(f"Adding bet event: {event_name} for {game_id} with odds {odds}")
        db = SessionLocal()
        try:
            existing_bet_event = (
                db.query(BetEvent)
                .filter(
                    BetEvent.event == event_name,
                    BetEvent.game_id == game_id,
                )
                .first()
            )
            if not existing_bet_event:
                new_bet_event = BetEvent(
                    event=event_name,
                    odds=odds,
                    game_id=game_id,
                )
                db.add(new_bet_event)
                db.commit()
                logger.info(
                    f"Added new bet event: {event_name} for {game_id} with odds {odds}"
                )
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding odd: {str(e)}")
            raise
        finally:
            db.close()

    async def add_game(self, home_team, away_team, datetime, sport_id, league_id):
        logger.info(f"Adding game: {home_team} vs {away_team} with datetime {datetime}")
        db = SessionLocal()
        try:
            existing_game = (
                db.query(Game)
                .filter(
                    Game.home_team == home_team,
                    Game.away_team == away_team,
                    Game.datetime == datetime,
                    Game.sport_id == sport_id,
                    Game.league_id == league_id,
                )
                .first()
            )
            if not existing_game:
                new_game = Game(
                    home_team=home_team,
                    away_team=away_team,
                    datetime=datetime,
                    sport_id=sport_id,
                    league_id=league_id,
                )
                db.add(new_game)
                db.commit()
                db.refresh(
                    new_game
                )  # Refresh to ensure the object is bound to the session
                logger.info(
                    f"Added new game: {home_team} vs {away_team} with datetime {datetime}"
                )
                return new_game
            else:
                db.refresh(
                    existing_game
                )  # Refresh existing game to ensure it's bound to session
                return existing_game
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding game: {str(e)}")
            raise
        finally:
            db.close()

    async def cleanup_old_games(self):
        """
        Remove all games and their associated bet events that are older than 2 days.
        This function handles the cascade deletion properly by first removing bet events,
        then removing the games.
        """
        db = SessionLocal()
        try:
            # Calculate cutoff date (today - 2 days)
            cutoff_date = datetime.now() - timedelta(days=2)

            logger.info(f"Starting cleanup of games older than {cutoff_date}")

            # First, find all games older than cutoff date
            old_games = db.query(Game).filter(Game.datetime < cutoff_date).all()

            if not old_games:
                logger.info("No old games found to clean up")
                return

            logger.info(f"Found {len(old_games)} games to clean up")

            # Count bet events that will be deleted
            total_bet_events = 0
            for game in old_games:
                bet_events_count = (
                    db.query(BetEvent).filter(BetEvent.game_id == game.id).count()
                )
                total_bet_events += bet_events_count

            logger.info(
                f"Will delete {total_bet_events} bet events associated with old games"
            )

            # Delete all bet events associated with old games
            deleted_bet_events = (
                db.query(BetEvent)
                .filter(BetEvent.game_id.in_([game.id for game in old_games]))
                .delete(synchronize_session=False)
            )

            logger.info(f"Deleted {deleted_bet_events} bet events")

            # Delete the old games
            deleted_games = (
                db.query(Game)
                .filter(Game.datetime < cutoff_date)
                .delete(synchronize_session=False)
            )

            logger.info(f"Deleted {deleted_games} games")

            db.commit()
            logger.info(
                f"Cleanup completed successfully: {deleted_games} games and {deleted_bet_events} bet events removed"
            )

            return {
                "deleted_games": deleted_games,
                "deleted_bet_events": deleted_bet_events,
                "cutoff_date": cutoff_date.isoformat(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error during cleanup: {str(e)}")
            raise
        finally:
            db.close()

    async def refresh_events(self, only_one=False, only_one_by_key=None):
        """
        Clean old games and download new events in one operation.
        This function first removes games older than 2 days, then downloads
        new events and odds for all leagues with download=True.

        Args:
            only_one: If True, only download events for the first league
            only_one_by_key: If provided, only download events for the league with this api_league_key

        Returns:
            dict: Summary of cleanup and download operations
        """
        try:
            logger.info(
                "Starting refresh_events: cleaning old games and downloading new events"
            )

            # Step 1: Clean up old games
            logger.info("Step 1: Cleaning up old games...")
            cleanup_result = await self.cleanup_old_games()

            if cleanup_result:
                logger.info(
                    f"Cleanup completed: {cleanup_result['deleted_games']} games and "
                    f"{cleanup_result['deleted_bet_events']} bet events removed"
                )
            else:
                logger.info("No old games to clean up")

            # Step 2: Download new events
            logger.info("Step 2: Downloading new events and odds...")
            await self.download_events_and_odds(
                only_one=only_one, only_one_by_key=only_one_by_key
            )

            logger.info("Refresh events completed successfully!")

            return {
                "cleanup": cleanup_result,
                "download": "completed",
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error during refresh_events: {str(e)}")
            raise


odds_data_service = OddsDataService()
