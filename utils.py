import datetime
import json
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

try:
    from aqt import mw
except:
    mw = None

def get_addon_folder():
    return os.path.dirname(os.path.abspath(__file__))

def get_selections_file():
    addon_folder = get_addon_folder()
    return os.path.join(addon_folder, "user_selections.json") if addon_folder else ""

def load_selections():
    try:
        selections_file = get_selections_file()
        if not selections_file or not os.path.exists(selections_file):
            return []
        with open(selections_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            dates = data.get("selectedDates", [])
            valid_dates = []
            for date_str in dates:
                try:
                    datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    valid_dates.append(date_str)
                except ValueError:
                    logger.warning(f"Invalid date: {date_str}")
            return valid_dates
    except json.JSONDecodeError as e:
        logger.error(f"JSON error: {e}")
        return []
    except IOError as e:
        logger.error(f"IO error: {e}")
        return []
    except Exception as e:
        logger.error(f"Load error: {e}", exc_info=True)
        return []

def save_selections(dates):
    try:
        selections_file = get_selections_file()
        if not selections_file:
            return False
        validated = []
        for date_str in dates:
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                validated.append(date_str)
            except ValueError:
                logger.warning(f"Skip invalid: {date_str}")
        MAX_SELECTIONS = 10000
        if len(validated) > MAX_SELECTIONS:
            validated = validated[:MAX_SELECTIONS]
        with open(selections_file, 'w', encoding='utf-8') as f:
            json.dump({"selectedDates": sorted(validated)}, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Save error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected save error: {e}", exc_info=True)
        return False

def get_review_data(months_back=36):
    data = {}
    try:
        if not isinstance(months_back, int) or months_back < 1 or months_back > 36:
            months_back = 36
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30 * months_back)
        current_date = start_date
        while current_date <= today:
            data[current_date.strftime("%Y-%m-%d")] = 0
            current_date += datetime.timedelta(days=1)
        if not mw or not mw.col:
            return data
        try:
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int((today + datetime.timedelta(days=1)).timestamp() * 1000)
            revlog_data = mw.col.db.execute(
                "SELECT id FROM revlog WHERE id >= ? AND id <= ?",
                start_ts, end_ts
            ).fetchall()
            MAX_REVIEWS_PER_DAY = 5000
            for (timestamp,) in revlog_data:
                try:
                    review_date = datetime.datetime.fromtimestamp(timestamp / 1000).date()
                    date_str = review_date.strftime("%Y-%m-%d")
                    if date_str in data:
                        data[date_str] += 1
                        if data[date_str] > MAX_REVIEWS_PER_DAY:
                            data[date_str] = MAX_REVIEWS_PER_DAY
                except (ValueError, OSError):
                    continue
            logger.info(f"Fetched data for {len(data)} days")
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
        return data
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return data
