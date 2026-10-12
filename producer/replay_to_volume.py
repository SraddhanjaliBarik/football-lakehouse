from dotenv import load_dotenv
load_dotenv()

import io, json, time, requests
from databricks.sdk import WorkspaceClient

MATCH_ID, SPEED, WINDOW = 3943043, 60, 5   # 60x speed, 5 s batches
VOLUME_DIR = "/Volumes/football/bronze/landing"
URL = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{MATCH_ID}.json"

w = WorkspaceClient()
print("Connected as:", w.current_user.me().user_name)

print("Downloading match events...")
events = requests.get(URL, timeout=30).json()
events.sort(key=lambda e: (e["period"], e["minute"], e["second"], e["index"]))
for e in events:
    e["match_id"] = MATCH_ID
    e["t"] = (e["minute"] * 60 + e["second"]) / SPEED
print(f"Loaded {len(events)} events")

n, i, start = 0, 0, time.time()
while i < len(events):
    cutoff = (time.time() - start) + WINDOW
    batch = []
    while i < len(events) and events[i]["t"] <= cutoff:
        batch.append(events[i])
        i += 1
    if batch:
        body = "\n".join(json.dumps(e) for e in batch).encode()
        path = f"{VOLUME_DIR}/m{MATCH_ID}_{n:06d}.json"
        w.files.upload(path, io.BytesIO(body), overwrite=True)
        print(f"Uploaded {path} ({len(batch)} events, {i}/{len(events)} total)")
        n += 1
    time.sleep(WINDOW)

print("Done.")