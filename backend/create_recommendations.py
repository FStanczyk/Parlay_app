import sys
import random
from decimal import Decimal
from sqlalchemy import or_
from app.core.database import SessionLocal
from app.models.tipster import Tipster
from app.models.tipster_tier import TipsterTier
from app.models.bet_event import BetEvent, BetResult
from app.models.bet_recommendation import BetRecommendation
from app.models.game import Game

DESCRIPTIONS = [
    "Strong value bet here, backing the favourite at a good price.",
    "Great odds for what should be a comfortable win.",
    "Home advantage should play a big role in this one.",
    "Both teams have been scoring freely — leaning on the over.",
    "Key players returning from injury boosts this side considerably.",
    "The form table heavily favours this pick right now.",
    "Historically this fixture produces goals — taking over 2.5.",
    "Low odds but very high confidence on this one.",
    "Contrarian pick — the market is undervaluing the away side.",
    None,
    None,
    None,
]


def create_recommendations(start_id: int, end_id: int, min_recs: int = 3, max_recs: int = 10):
    db = SessionLocal()
    try:
        unresolved_events = (
            db.query(BetEvent)
            .join(BetEvent.game)
            .filter(
                or_(
                    BetEvent.result.in_([BetResult.TO_RESOLVE, BetResult.UNKNOWN]),
                    BetEvent.result.is_(None),
                )
            )
            .all()
        )

        if not unresolved_events:
            print("❌ No unresolved bet events found. Run ingestion first.")
            return

        print(f"Found {len(unresolved_events)} unresolved bet events.")

        tipsters = (
            db.query(Tipster)
            .filter(Tipster.id >= start_id, Tipster.id <= end_id)
            .all()
        )

        if not tipsters:
            print(f"❌ No tipsters found with IDs between {start_id} and {end_id}.")
            return

        print(f"Found {len(tipsters)} tipsters (IDs {start_id}–{end_id}).")

        total_created = 0
        total_skipped = 0

        for tipster in tipsters:
            tiers = (
                db.query(TipsterTier)
                .filter(TipsterTier.tipster_id == tipster.id)
                .all()
            )
            tier_choices = [None] + [t.id for t in tiers]

            existing_event_ids = set(
                row.bet_event_id
                for row in db.query(BetRecommendation.bet_event_id)
                .filter(BetRecommendation.tipster_id == tipster.id)
                .all()
            )

            available = [e for e in unresolved_events if e.id not in existing_event_ids]

            if not available:
                print(f"  Tipster {tipster.id}: no available events, skipping.")
                continue

            count = random.randint(min_recs, max_recs)
            count = min(count, len(available))
            sampled = random.sample(available, count)

            created = 0
            for event in sampled:
                tier_id = random.choice(tier_choices)

                existing = (
                    db.query(BetRecommendation)
                    .filter(
                        BetRecommendation.tipster_id == tipster.id,
                        BetRecommendation.bet_event_id == event.id,
                        BetRecommendation.tipster_tier_id == tier_id,
                    )
                    .first()
                )
                if existing:
                    total_skipped += 1
                    continue

                stake = Decimal(str(round(random.uniform(0.5, 5.0), 1))) if random.random() > 0.3 else None
                description = random.choice(DESCRIPTIONS)

                rec = BetRecommendation(
                    tipster_id=tipster.id,
                    bet_event_id=event.id,
                    tipster_tier_id=tier_id,
                    tipster_description=description,
                    stake=stake,
                )
                db.add(rec)
                created += 1
                total_created += 1

            db.flush()
            print(f"  Tipster {tipster.id}: created {created} recommendations.")

        db.commit()
        print(f"\n✅ Done! Created {total_created} recommendations, skipped {total_skipped} duplicates.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    start_id = 1
    end_id = 100
    min_recs = 3
    max_recs = 10

    if len(sys.argv) > 1:
        try:
            start_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid start_id. Using default: {start_id}")

    if len(sys.argv) > 2:
        try:
            end_id = int(sys.argv[2])
        except ValueError:
            print(f"Invalid end_id. Using default: {end_id}")

    if len(sys.argv) > 3:
        try:
            min_recs = int(sys.argv[3])
        except ValueError:
            print(f"Invalid min. Using default: {min_recs}")

    if len(sys.argv) > 4:
        try:
            max_recs = int(sys.argv[4])
        except ValueError:
            print(f"Invalid max. Using default: {max_recs}")

    print(f"Creating {min_recs}–{max_recs} recommendations for tipsters {start_id}–{end_id}")
    create_recommendations(start_id, end_id, min_recs, max_recs)
