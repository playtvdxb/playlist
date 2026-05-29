import urllib3
import urllib.parse
import json
import time

# =========================
# INIT
# =========================
http = urllib3.PoolManager()
playlist = ["#EXTM3U"]

allowed_langs = {
    "ENG", "HIN", "TAM", "MAR", "BEN", "TEL",
    "KAN", "BHO", "GUA", "PUN", "ASS", "URD"
}

# =========================
# SAFE REQUEST FUNCTION
# =========================
def get_json(url, headers, name):
    for attempt in range(3):
        try:
            resp = http.request("GET", url, headers=headers)
            raw = resp.data.decode("utf-8", errors="ignore").strip()

            if resp.status != 200:
                print(f"[{name}] HTTP {resp.status} retry {attempt+1}")
                time.sleep(2)
                continue

            if not raw or not raw.startswith("{"):
                print(f"[{name}] invalid response retry {attempt+1}: {raw[:80]}")
                time.sleep(2)
                continue

            return json.loads(raw)

        except Exception as e:
            print(f"[{name}] error retry {attempt+1}: {e}")
            time.sleep(2)

    raise Exception(f"{name} failed after retries")


# =========================
# TOKEN API
# =========================
token_url = "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta"

token_headers = {
    "Accept": "application/json, text/plain, */*",
    "Tenant-Code": "yuppfast",
    "Origin": "https://www.yupptv.com",
    "Referer": "https://www.yupptv.com/",
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

token_data = get_json(token_url, token_headers, "TOKEN")

sessionid = token_data.get("response", {}).get("sessionId")

if not sessionid:
    raise Exception("Session ID not received from API")

print("Session ID OK")


# =========================
# CHANNEL LIST API
# =========================
channels_url = "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD"

channels_headers = {
    "Accept": "application/json, text/plain, */*",
    "Tenant-Code": "yuppfast",
    "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
    "Origin": "https://www.yupptv.com",
    "Referer": "https://www.yupptv.com/",
    "Session-Id": sessionid,
    "User-Agent": "Mozilla/5.0"
}

channels_data = get_json(channels_url, channels_headers, "CHANNELS")

channels = channels_data.get("response", {}).get("data", [])

if not channels:
    raise Exception("No channels found in API response")


# =========================
# PROCESS CHANNELS
# =========================
for ch in channels:

    try:
        lang = ch.get("langCode") or ch.get("display", {}).get("langCode")

        if lang not in allowed_langs:
            continue

        path = ch["target"]["path"]
        epg = ch["id"]
        name = ch["display"]["title"]

        logo = ch["display"]["imageUrl"]
        logo = logo.replace(
            "common,",
            "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/"
        )

        playlist.append(
            f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )

        encodedpath = urllib.parse.quote_plus(path)

        stream_url = f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}"

        stream_headers = {
            "Accept": "application/json, text/plain, */*",
            "Tenant-Code": "yuppfast",
            "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
            "Origin": "https://www.yupptv.com",
            "Referer": "https://www.yupptv.com/",
            "Session-Id": sessionid,
            "Accept-Language": (lang or "eng").lower(),
            "User-Agent": "Mozilla/5.0"
        }

        stream_data = get_json(stream_url, stream_headers, "STREAM")

        if stream_data.get("status") is True:
            streams = stream_data.get("response", {}).get("streams", [])

            urls = [s.get("url") for s in streams if s.get("url")]

            playlist.append(urls[0] if urls else "")
        else:
            playlist.append("")

    except Exception as e:
        print("Channel error:", e)
        playlist.append("")
        continue


# =========================
# SAVE M3U
# =========================
with open("yupptvfast.m3u", "w", encoding="utf-8") as f:
    for line in playlist:
        f.write(line + "\n")

print("✅ M3U generated successfully!")
