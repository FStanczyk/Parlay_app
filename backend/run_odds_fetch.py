#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.odds_data_service import odds_data_service


async def main():
    result = await odds_data_service.refresh_events()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
