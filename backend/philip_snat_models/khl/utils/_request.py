import requests
import time


def req(url, max_retries=1, delay=3):
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(delay)
            else:
                print(f"Request failed after {max_retries + 1} attempts. Last error: {e}")
                return None
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(delay)
            else:
                print(f"Request failed after {max_retries + 1} attempts. Last error: {e}")
                return None
    return None
