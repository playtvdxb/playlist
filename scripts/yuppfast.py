import urllib3
import urllib.parse
import json

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
# TOKEN REQUEST
# =========================
token_url = "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta"

token_resp = http.request(
    "GET",
    token_url,
    headers={
        "Accept": "application/json, text/plain, */*",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "User-Agent": "Mozilla/5.0"
    }
)

token_data = json.loads(token_resp.data.decode("utf-8"))
sessionid = token_data["response"]["sessionId"]

# =========================
# CHANNEL LIST
# =========================
channels_url = "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD"

channels_resp = http.request(
    "GET",
    channels_url,
    headers={
        "Accept": "application/json, text/plain, */*",
        "Tenant-Code": "yuppfast",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0"
    }
)

channels_data = json.loads(channels_resp.data.decode("utf-8"))

# =========================
# PROCESS CHANNELS
# =========================
for ch in channels_data["response"]["data"]:

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

        # M3U metadata
        playlist.append(
            f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )

        encodedpath = urllib.parse.quote_plus(path)

        # =========================
        # STREAM REQUEST
        # =========================
        stream_resp = http.request(
            "GET",
            f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Tenant-Code": "yuppfast",
                "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
                "Origin": "https://www.yupptv.com",
                "Referer": "https://www.yupptv.com/",
                "Session-Id": sessionid,
                "Accept-Language": lang.lower() if lang else "eng",
                "User-Agent": "Mozilla/5.0"
            }
        )

        stream_json = json.loads(stream_resp.data.decode("utf-8"))

        # FIX: collect all URLs properly
        if stream_json.get("status") is True:
            streams = stream_json.get("response", {}).get("streams", [])

            urls = [s.get("url") for s in streams if s.get("url")]

            if urls:
                playlist.append(urls[0])
            else:
                playlist.append("")

        else:
            playlist.append("")

    except Exception:
        # Never break playlist generation
        playlist.append("")
        continue

# =========================
# SAVE FILE
# =========================
with open("yupptvfast.m3u", "w", encoding="utf-8") as f:
    for line in playlist:
        f.write(line + "\n")

print("M3U playlist generated successfully!")
