import requests
import time


def req(url, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            if attempt < max_attempts - 1:
                time.sleep(3)
            else:
                print(f"Failed to fetch {url} after {max_attempts} attempts: {e}")
                return None
    return None
