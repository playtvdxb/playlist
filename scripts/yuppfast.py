import urllib3
import urllib.parse
import json

http = urllib3.PoolManager()

playlist = ["#EXTM3U"]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Tenant-Code": "yuppfast",
    "Origin": "https://www.yupptv.com",
    "Referer": "https://www.yupptv.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

# ============================================
# GET TOKEN
# ============================================

token_url = (
    "https://yuppfast-api.revlet.net/service/api/v1/get/token"
    "?tenant_code=yuppfast"
    "&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c"
    "&product=yuppfast"
    "&device_id=5"
    "&device_sub_type=Chrome,145.0.0.0,Windows"
    "&client_app_version=1"
    "&timezone=Asia/Calcutta"
)

resp = http.request("GET", token_url, headers=HEADERS)

try:
    jsonresp = json.loads(resp.data.decode("utf-8"))
    sessionid = jsonresp["response"]["sessionId"]
except:
    raise Exception("Token fetch failed")

# ============================================
# CHANNEL LIST
# ============================================

channel_headers = HEADERS.copy()
channel_headers.update({
    "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
    "Session-Id": sessionid
})

channels_url = (
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels"
    "?filter=genreCode:all;"
    "langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD"
)

resp = http.request("GET", channels_url, headers=channel_headers)

try:
    jsonresp = json.loads(resp.data.decode("utf-8"))
except:
    raise Exception("Channel list failed")

# ============================================
# DETECT STREAM
# ============================================

def get_best_stream(streams):
    if not streams:
        return ""

    best = ""
    best_score = -1

    for s in streams:
        url = s.get("url", "")
        if not url:
            continue

        lower = url.lower()
        score = 0

        # HLS preference
        if ".m3u8" in lower:
            score += 500

        # quality hints
        if "1080" in lower:
            score += 300
        elif "720" in lower:
            score += 200
        elif "480" in lower:
            score += 100

        # avoid bad streams
        if "ad" in lower:
            score -= 1000
        if "low" in lower:
            score -= 300

        if score > best_score:
            best_score = score
            best = url

    return best

# ============================================
# PROCESS CHANNELS
# ============================================

for c in jsonresp["response"]["data"]:

    try:
        path = c["target"]["path"]
        epg = c["id"]
        name = c["display"]["title"]

        logo = c["display"]["imageUrl"].replace(
            "common,",
            "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/"
        )

        encodedpath = urllib.parse.quote_plus(path)

        stream_url = (
            "https://yuppfast-api.revlet.net/service/api/v1/page/stream"
            f"?path={encodedpath}"
        )

        resp = http.request("GET", stream_url, headers=channel_headers)

        try:
            stream = json.loads(resp.data.decode("utf-8"))
        except:
            stream = {}

        final_stream = ""

        if stream.get("status") and "streams" in stream.get("response", {}):
            final_stream = get_best_stream(stream["response"]["streams"])

        playlist.append(
            f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )

        playlist.append(final_stream)

        print("Added:", name)

    except Exception as e:
        print("Error channel:", e)

# ============================================
# WRITE FILE
# ============================================

with open("yupptvfast.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(playlist))

print("DONE: Playlist generated")
