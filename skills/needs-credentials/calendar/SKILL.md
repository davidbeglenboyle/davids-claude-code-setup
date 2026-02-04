---
name: calendar
description: |
  Manage your Google Calendar via Python API. Use when asked to:
  - Add flights from booking emails or text
  - Add travel blocks before/after flights
  - Query calendar for availability, conflicts, or upcoming events
  - Create reminders for car rentals, pickups, etc.

  Triggers: "add this flight", "check my calendar", "when am I free",
  "add travel blocks", "what's on my calendar", "find my flights"
---

# Calendar Management

## Setup

Credentials: `~/.config/google-calendar/`
- `credentials.json` — OAuth client config (see SETUP.md)
- `token.json` — Auth token (auto-refreshes)

## Quick Python Access

```python
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = os.path.expanduser("~/.config/google-calendar/token.json")
creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

# Query events
events = service.events().list(
    calendarId='primary',
    timeMin="2026-02-01T00:00:00Z",
    timeMax="2026-02-28T23:59:59Z",
    singleEvents=True,
    orderBy='startTime',
    q='search term'  # optional
).execute()

# Create event
event = {
    'summary': 'Event title',
    'start': {'dateTime': '2026-02-15T10:00:00Z', 'timeZone': 'UTC'},
    'end': {'dateTime': '2026-02-15T11:00:00Z', 'timeZone': 'UTC'},
    'location': 'Optional location',
    'description': 'Optional notes'
}
service.events().insert(calendarId='primary', body=event).execute()

# Update event
service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
```

## Adding Flights

When given flight details (from email or text):

1. **Extract**: flight number, date, departure time, arrival time, route, booking ref
2. **Create event** with:
   - Summary: `✈️ {flight} {origin} → {dest}` (e.g., `✈️ VS157 LHR → BOS`)
   - Start: departure time (local to origin, converted to UTC)
   - End: arrival time (local to destination, converted to UTC)
   - Location: departure airport
   - Description: airline, booking ref, arrival info with timezones noted

3. **Add travel blocks**: e.g., 3hr before departure, 2hr after arrival as "Travel"

## Timezone Reference

```python
from zoneinfo import ZoneInfo
from datetime import datetime

# Convert local time to UTC
local_tz = ZoneInfo("America/New_York")
local_time = datetime(2026, 3, 15, 10, 0, tzinfo=local_tz)
utc_time = local_time.astimezone(ZoneInfo('UTC'))
```

Common zones: `Europe/London`, `America/New_York`, `America/Los_Angeles`, `Asia/Tokyo`

## Car Rental Reminders

Create event at pickup time:
- Summary: `🚗 Car Pickup - {location} #{booking}`
- Duration: 1 hour
- Location: airport/rental location
- Description: booking ref, return date/time, "bring: license, credit card, confirmation"

## Custom Scripts (Optional)

You can create helper scripts for recurring tasks:

| Script | Purpose |
|--------|---------|
| `adjust_sleep_for_travel.py` | Shift sleep blocks to local timezone for trips |
| `add_travel_blocks.py` | Add buffer time before/after all flights |

Store in `~/.config/google-calendar/` alongside credentials.
