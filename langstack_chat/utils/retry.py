import time
from openai import APIConnectionError, APIError, RateLimitError, APITimeoutError
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

TERMINAL_CODES = {401, 402, 403, 404}

def with_retry(fn, max_retries=3, wait=5):
    for attempt in range(1, max_retries + 1):
        try:
            return fn()

        except RateLimitError as e:
            logger.warning("Rate limit attempt %d/%d — waiting %ds", attempt, max_retries, wait * attempt)
            time.sleep(wait * attempt)
            continue

        except APITimeoutError as e:
            logger.warning("Timeout attempt %d/%d: %s", attempt, max_retries, e)

        except APIConnectionError as e:
            logger.warning("Connection error attempt %d/%d: %s", attempt, max_retries, e)

        # except APIError as e:
        #     if e.status_code in TERMINAL_CODES:
        #         logger.error("Terminal error %s — stopping.", e.status_code)
        #         raise
        #     logger.warning("APIError attempt %d/%d: %s", attempt, max_retries, e)

        if attempt < max_retries:
            logger.info("Retrying in %ds...", wait)
            time.sleep(wait)

    raise RuntimeError(f"Failed after {max_retries} attempts.")
