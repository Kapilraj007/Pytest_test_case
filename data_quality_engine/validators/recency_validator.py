
from datetime import datetime

def calculate_recency(last_updated_date):
    date = datetime.strptime(last_updated_date, "%Y-%m-%d")
    today = datetime.today()

    if date > today:
        raise ValueError("ERR_DATE_INVALID")

    months_diff = (today.year - date.year) * 12 + today.month - date.month

    if months_diff <= 3:
        return {"recency_status": "Recent"}
    elif 4 <= months_diff <= 12:
        return {"recency_status": "Acceptable"}
    else:
        return {"recency_status": "Outdated", "trigger_revalidation": True}
