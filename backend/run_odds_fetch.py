#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.odds_data_service import odds_data_service


async def main():
    """Run the test function"""
    print("Testing API call to /odds endpoint...")

    result = await odds_data_service.download_events_and_odds(
        only_one_by_key="icehockey_nhl"
    )

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
