import urllib3
import urllib
import json

playlist = ["#EXTM3U"]

http = urllib3.PoolManager()

# =========================
# SAFE JSON FUNCTION
# =========================
def safe_json(resp, name):
    raw = resp.data.decode("utf-8", errors="ignore").strip()

    if not raw:
        raise Exception(f"{name} returned EMPTY response")

    if not raw.startswith("{"):
        raise Exception(f"{name} invalid response: {raw[:200]}")

    return json.loads(raw)

# =========================
# TOKEN REQUEST
# =========================
token_resp = http.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "User-Agent": "Mozilla/5.0"
    }
)

token_data = safe_json(token_resp, "TOKEN")
sessionid = token_data.get("response", {}).get("sessionId")

if not sessionid:
    raise Exception("Session ID missing from token response")

# =========================
# CHANNEL REQUEST
# =========================
channels_resp = http.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0"
    }
)

channels_data = safe_json(channels_resp, "CHANNELS")

channels = channels_data.get("response", {}).get("data", [])

if not channels:
    raise Exception("No channels received")

# =========================
# LANGUAGE SUPPORT
# =========================
allowed_langs = {
    "ENG","HIN","TAM","MAR","BEN","TEL",
    "KAN","BHO","GUA","PUN","ASS","URD"
}

# =========================
# PROCESS CHANNELS
# =========================
for ch in channels:

    try:
        lang = ch.get("langCode") or ch.get("display", {}).get("langCode") or "ENG"

        # language filter
        if lang not in allowed_langs:
            continue

        path = ch["target"]["path"]
        epg = ch["id"]
        name = ch["display"]["title"]

        logo = ch["display"]["imageUrl"].replace(
            "common,",
            "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/"
        )

        playlist.append(
            f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )

        encodedpath = urllib.parse.quote_plus(path)

        stream_resp = http.request(
            "GET",
            f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
                "Tenant-Code": "yuppfast",
                "Origin": "https://www.yupptv.com",
                "Referer": "https://www.yupptv.com/",
                "Session-Id": sessionid,
                "User-Agent": "Mozilla/5.0"
            }
        )

        stream_data = safe_json(stream_resp, "STREAM")

        if stream_data.get("status") is True:
            streams = stream_data.get("response", {}).get("streams", [])
            urls = [s.get("url") for s in streams if s.get("url")]

            playlist.append(urls[0] if urls else "")
        else:
            playlist.append("")

    except Exception:
        playlist.append("")
        continue

# =========================
# SAVE FILE
# =========================
with open("yupptvfast.m3u", "w", encoding="utf-8") as f:
    for line in playlist:
        f.write(line + "\n")

print("M3U generated successfully")
