import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import TypedDict

from langgraph.graph import StateGraph
from ingest import get_activities

ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")

DAYS_HE = {
    0: "שני", 1: "שלישי", 2: "רביעי",
    3: "חמישי", 4: "שישי", 5: "שבת", 6: "ראשון"
}

CATEGORY_KEYWORDS = {
    "ספורט": ["ספורט", "כדור", "שחייה", "כושר", "יוגה", "ריצה", "ג'ודו", "ספינינג", "פילאטיס", "התעמלות", "טאי צ'י"],
    "אמנות": ["אמנות", "ציור", "מוזיקה", "תיאטרון", "מחול", "ריקוד", "גיטרה", "מקהלה", "רישום"],
    "שפות": ["שפות", "אנגלית", "ערבית", "צרפתית", "ספרדית"],
    "גיל הזהב": ["גיל הזהב", "קשישים"],
    "הורים וילדים": ["הורים וילדים", "הורים"],
}

AGE_GROUPS = {
    "תינוקות": (0, 3),
    "גיל הרך": (0, 6),
    "ילדים": (7, 12),
    "נוער": (13, 18),
    "מבוגרים": (19, 60),
    "גיל הזהב": (61, 120),
}

class AgentState(TypedDict, total=False):
    user_input: str
    filters: dict
    result: str

def parse_start_time(start_time: str):
    """מחזיר datetime בשעון ישראל, או None אם נכשל."""
    if not start_time:
        return None
    try:
        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        return dt.astimezone(ISRAEL_TZ)
    except Exception:
        return None

def extract_filters(state: AgentState) -> AgentState:
    text = state["user_input"]
    filters = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            filters["category"] = category
            break

    for group_name, (min_a, max_a) in AGE_GROUPS.items():
        if group_name in text:
            filters["age_range"] = (min_a, max_a)
            break

    # גיל
    age_match = re.search(
        r'בן\s*(\d+)'
        r'|בת\s*(\d+)'
        r'|בגיל\s*(\d+)'
        r'|גיל\s*(\d+)'
        r'|(\d+)\s*שנ',
        text
    )
    if age_match:
        filters["age"] = int(next(g for g in age_match.groups() if g is not None))

    # שעה
    hour_match = re.search(r"אחרי\s*(\d+):?(\d*)", text)
    if hour_match:
        hour = int(hour_match.group(1))
        minutes = int(hour_match.group(2)) if hour_match.group(2) else 0
        filters["after_minutes"] = hour * 60 + minutes

    # יום בשבוע
    days = {
        "ראשון": 6, "שני": 0, "שלישי": 1,
        "רביעי": 2, "חמישי": 3, "שישי": 4
    }
    for day_name, day_num in days.items():
        if day_name in text:
            filters["day"] = day_num
            break

    state["filters"] = filters
    return state


def fetch_activities(state: AgentState) -> AgentState:
    activities = get_activities()
    filters = state.get("filters", {})
    results = []
    lines = []

    for a in activities:
        # סינון קטגוריה - גמיש, מתאים חלקי
        if "category" in filters:
            activity_cat = a.get("category", "")
            filter_cat = filters["category"]
            # תואם אם המחרוזת מכילה את הקטגוריה (בשני הכיוונים)
            if filter_cat not in activity_cat and activity_cat not in filter_cat:
                continue

        # סינון גיל
        if "age" in filters:
            try:
                user_age = int(filters["age"])
                min_age = int(str(a.get("min_age") or 0).strip())
                max_age = int(str(a.get("max_age") or 120).strip())
                if not (min_age <= user_age <= max_age):
                    continue
            except (ValueError, TypeError):
                continue

        elif "age_range" in filters:
            try:
                filt_min, filt_max = filters["age_range"]
                min_age = int(str(a.get("min_age") or 0).strip())
                max_age = int(str(a.get("max_age") or 120).strip())
                # כולל את הפעילות אם יש חפיפה בין טווחי הגיל
                if max_age < filt_min or min_age > filt_max:
                    continue
            except (ValueError, TypeError):
                continue

        # סינון שעה
        dt_local = parse_start_time(a.get("start_time", ""))

        if "after_minutes" in filters:
            if dt_local is None:
                continue
            start_minutes = dt_local.hour * 60 + dt_local.minute
            if start_minutes < filters["after_minutes"]:
                continue

        # סינון יום
        if "day" in filters:
            if dt_local is None:
                continue
            if dt_local.weekday() != filters["day"]:
                continue
        results.append((a, dt_local))

        # מיון לפי שעה
        results.sort(key=lambda x: (x[1].hour * 60 + x[1].minute) if x[1] else 0)

        if not results:
            state["result"] = "לא נמצאו פעילויות מתאימות לחיפוש שלך."
            return state
        count = len(results)
        if count == 1:
            count_str = "נמצאה פעילות **אחת**"
        else:
            count_str = f"נמצאו **{count} פעילויות**"
        lines = [f"{count_str}:\n"]

        for i, (a, dt_local) in enumerate(results, 1):
            # פורמט שעה ויום
            if dt_local:
                day_name = DAYS_HE.get(dt_local.weekday(), "")
                time_str = dt_local.strftime("%H:%M")
                if a.get("is_recurring"):
                    schedule = f"כל יום {day_name} בשעה {time_str}"
                else:
                    date_str = dt_local.strftime("%d/%m/%Y")
                    schedule = f"יום {day_name} {date_str} בשעה {time_str}"
            else:
                schedule = ""

            block = f"**{i}. {a.get('title', '')}**"
            if schedule:
                block += f"\n🗓 {schedule}"
            if a.get("instructor"):
                block += f"\n👤 מדריך: {a['instructor']}"
            if a.get("price"):
                block += f"\n💰 מחיר: {a['price']} ₪"
            if a.get("min_age") and a.get("max_age"):
                block += f"\n🎂 גילאים: {a['min_age']}-{a['max_age']}"
            if a.get("location"):
                block += f"\n📍 מיקום: {a['location']}"
            lines.append(block)

    state["result"] = "\n\n---\n\n".join(lines)
    return state


graph = StateGraph(AgentState)
graph.add_node("extract_filters", extract_filters)
graph.add_node("fetch_activities", fetch_activities)
graph.set_entry_point("extract_filters")
graph.add_edge("extract_filters", "fetch_activities")
graph.set_finish_point("fetch_activities")
app = graph.compile()