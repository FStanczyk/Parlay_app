import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.tipster import Tipster

FIRST_NAMES = [
    "James",
    "John",
    "Robert",
    "Michael",
    "William",
    "David",
    "Richard",
    "Joseph",
    "Thomas",
    "Charles",
    "Christopher",
    "Daniel",
    "Matthew",
    "Anthony",
    "Mark",
    "Donald",
    "Steven",
    "Paul",
    "Andrew",
    "Joshua",
    "Mary",
    "Patricia",
    "Jennifer",
    "Linda",
    "Barbara",
    "Elizabeth",
    "Susan",
    "Jessica",
    "Sarah",
    "Karen",
    "Nancy",
    "Lisa",
    "Betty",
    "Margaret",
    "Sandra",
    "Ashley",
    "Kimberly",
    "Emily",
    "Donna",
    "Michelle",
    "Emma",
    "Olivia",
    "Sophia",
    "Ava",
    "Isabella",
    "Mia",
    "Charlotte",
    "Amelia",
    "Harper",
    "Evelyn",
    "Liam",
    "Noah",
    "Oliver",
    "Elijah",
    "Lucas",
    "Mason",
    "Logan",
    "Alexander",
    "Ethan",
    "Jacob",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
    "Young",
    "Allen",
    "King",
    "Wright",
    "Scott",
    "Torres",
    "Nguyen",
    "Hill",
    "Flores",
    "Green",
    "Adams",
    "Nelson",
    "Baker",
    "Hall",
    "Rivera",
    "Campbell",
    "Mitchell",
    "Carter",
    "Roberts",
]

COUNTRIES = [
    "AF",
    "AL",
    "DZ",
    "AR",
    "AU",
    "AT",
    "BD",
    "BE",
    "BR",
    "BG",
    "CA",
    "CL",
    "CN",
    "CO",
    "HR",
    "CZ",
    "DK",
    "EG",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IS",
    "IN",
    "ID",
    "IE",
    "IL",
    "IT",
    "JP",
    "KE",
    "LV",
    "LT",
    "MY",
    "MX",
    "NL",
    "NZ",
    "NG",
    "NO",
    "PK",
    "PE",
    "PH",
    "PL",
    "PT",
    "RO",
    "RU",
    "SA",
    "RS",
    "SG",
    "SK",
    "SI",
    "ZA",
    "KR",
    "ES",
    "SE",
    "CH",
    "TH",
    "TR",
    "UA",
    "AE",
    "GB",
    "US",
    "VE",
    "VN",
]

SPORTS_TAGS = [
    "NBA",
    "NFL",
    "NHL",
    "MLB",
    "Soccer",
    "Tennis",
    "Boxing",
    "MMA",
    "F1",
    "Golf",
    "Cricket",
    "Rugby",
    "Volleyball",
    "Basketball",
    "Football",
    "Hockey",
]

BETTING_STYLES = [
    "Value Betting",
    "Arbitrage",
    "Live Betting",
    "Parlays",
    "Props",
    "Totals",
    "Spreads",
    "Moneyline",
    "High Risk",
    "Low Risk",
    "Long Term",
    "Daily Picks",
]

DESCRIPTIONS = [
    "Professional sports analyst with 10+ years of experience.",
    "Data-driven approach to sports betting. Statistics matter!",
    "High risk, high reward specialist. Not for the faint of heart.",
    "Conservative betting strategy focused on long-term profits.",
    "Live betting expert with quick analysis and fast picks.",
    "Former professional athlete turned betting analyst.",
    "Mathematical models and statistical analysis for consistent wins.",
    "Specializing in underdogs and value opportunities.",
    "Parlay master - turning small stakes into big wins.",
    "In-depth analysis and research for every pick.",
]


def generate_random_birthdate():
    """Generate random birthdate between 18 and 70 years ago"""
    start_date = datetime.now() - timedelta(days=70 * 365)
    end_date = datetime.now() - timedelta(days=18 * 365)
    time_between = end_date - start_date
    random_days = random.randrange(time_between.days)
    return start_date + timedelta(days=random_days)


def create_test_users(count: int = 100, expert_percentage: float = 0.0):
    """Create test users in the database

    Args:
        count: Number of users to create
        expert_percentage: Percentage (0.0-1.0) of users to make experts/tipsters
    """
    db: Session = SessionLocal()

    try:
        hashed_password = get_password_hash("alamakota")
        print(f"Creating {count} test users with password 'alamakota'...")

        created_count = 0
        attempts = 0
        max_attempts = count * 3
        created_users = []

        while created_count < count and attempts < max_attempts:
            attempts += 1

            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"

            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@test.com"

            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                continue

            country = random.choice(COUNTRIES)
            birthdate = generate_random_birthdate().date()

            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                country=country,
                birthdate=birthdate,
                is_active=True,
                is_admin=False,
            )

            db.add(user)
            db.flush()
            created_users.append(user)
            created_count += 1

            if created_count % 10 == 0:
                print(f"Created {created_count} users...")

        db.commit()
        print(f"\n✅ Successfully created {created_count} test users!")
        print(f"All users have password: alamakota")

        if expert_percentage > 0:
            num_experts = int(created_count * expert_percentage)
            if num_experts > 0:
                print(
                    f"\nCreating {num_experts} experts ({expert_percentage*100:.0f}%)..."
                )

                expert_users = random.sample(created_users, num_experts)
                experts_created = 0

                for user in expert_users:
                    existing_tipster = (
                        db.query(Tipster).filter(Tipster.user_id == user.id).first()
                    )
                    if existing_tipster:
                        continue

                    tag_1 = random.choice(SPORTS_TAGS)
                    tag_2 = random.choice(BETTING_STYLES)
                    tag_3 = random.choice(SPORTS_TAGS + BETTING_STYLES)

                    while tag_3 == tag_1 or tag_3 == tag_2:
                        tag_3 = random.choice(SPORTS_TAGS + BETTING_STYLES)

                    tipster = Tipster(
                        user_id=user.id,
                        description=random.choice(DESCRIPTIONS),
                        appreciation=random.randint(0, 100),
                        is_verified=random.random() < 0.1,
                        tag_1=tag_1,
                        tag_2=tag_2,
                        tag_3=tag_3,
                    )

                    db.add(tipster)
                    experts_created += 1

                    if experts_created % 5 == 0:
                        print(f"Created {experts_created} experts...")

                db.commit()
                print(f"✅ Successfully created {experts_created} experts!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating users: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = 100
    expert_percentage = 0.0

    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid count argument. Using default: {count}")

    if len(sys.argv) > 2:
        try:
            expert_percentage = float(sys.argv[2])
            if expert_percentage < 0 or expert_percentage > 1:
                print(f"Expert percentage must be between 0 and 1. Using default: 0.0")
                expert_percentage = 0.0
        except ValueError:
            print(f"Invalid expert percentage argument. Using default: 0.0")

    print(f"Configuration: {count} users, {expert_percentage*100:.0f}% will be experts")
    create_test_users(count, expert_percentage)
