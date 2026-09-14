"""Small US planning calendar; cultural/school dates require local confirmation."""
from datetime import date, timedelta

def nth_weekday(year, month, weekday, n):
    first = date(year, month, 1)
    return first + timedelta(days=(weekday-first.weekday()) % 7 + 7*(n-1))

def easter(year):
    # Gregorian computus.
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a+b-d-g+15) % 30
    i, k = c // 4, c % 4
    l = (32+2*e+2*i-h-k) % 7
    m = (a+11*h+22*l) // 451
    return date(year, (h+l-7*m+114)//31, (h+l-7*m+114)%31+1)

def upcoming(as_of, days_ahead=90, publish_lead_days=45):
    start = date.fromisoformat(as_of)
    if not 1 <= days_ahead <= 730 or not 0 <= publish_lead_days <= 365:
        raise ValueError("days_ahead must be 1..730; lead time must be 0..365")
    end = start + timedelta(days=days_ahead)
    result = []
    for year in range(start.year, end.year + 1):
        events = [("New Year's Day", date(year,1,1)), ("Valentine's Day",date(year,2,14)),
                  ("St. Patrick's Day",date(year,3,17)), ("Earth Day",date(year,4,22)),
                  ("Independence Day",date(year,7,4)), ("Halloween",date(year,10,31)),
                  ("Christmas",date(year,12,25)), ("Easter",easter(year)),
                  ("Martin Luther King Jr. Day",nth_weekday(year,1,0,3)),
                  ("Presidents Day",nth_weekday(year,2,0,3)),
                  ("Mother's Day",nth_weekday(year,5,6,2)),
                  ("Father's Day",nth_weekday(year,6,6,3)),
                  ("Labor Day",nth_weekday(year,9,0,1)),
                  ("Grandparents Day",nth_weekday(year,9,0,1)+timedelta(days=6)),
                  ("Thanksgiving",nth_weekday(year,11,3,4))]
        last_may = date(year,5,31)
        events.append(("Memorial Day",last_may-timedelta(days=last_may.weekday())))
        for name, event_date in events:
            if start <= event_date <= end:
                publish = event_date - timedelta(days=publish_lead_days)
                result.append({"event":name, "date":event_date.isoformat(),
                    "days_until_event":(event_date-start).days,
                    "suggested_publish_by":publish.isoformat(),
                    "suggested_manuscript_by":(publish-timedelta(days=45)).isoformat(),
                    "suggested_art_by":(publish-timedelta(days=21)).isoformat(),
                    "suggested_production_by":(publish-timedelta(days=7)).isoformat(),
                    "publish_window_missed":publish < start})
    return {"locale":"US starter calendar (actual dates, not observed federal dates)",
            "assumptions":"Deadlines are planning offsets, not measured demand or platform guarantees. "
                          "Confirm school breaks, seasonal dates and local customs separately.",
            "events":sorted(result, key=lambda x:x["date"])}
