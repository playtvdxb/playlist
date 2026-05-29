import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

http = urllib3.PoolManager()

# =========================
# TOKEN
# =========================
resp = http.request(
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

jsonresp = json.loads(resp.data.decode("utf-8"))
sessionid = jsonresp['response']['sessionId']

# =========================
# CHANNELS (LANGUAGE FIX ADDED)
# =========================
resp = http.request(
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

jsonresp = json.loads(resp.data.decode("utf-8"))

# =========================
# LANGUAGE FILTER (ADDED)
# =========================
allowed_langs = {"ENG","HIN","TAM","MAR","BEN","TEL","KAN","BHO","GUA","PUN","ASS","URD"}

for i in jsonresp['response']['data']:

    channel_data = i

    # 🔥 LANGUAGE SAFE CHECK (NEW)
    lang = (
        channel_data.get("langCode")
        or channel_data.get("display", {}).get("langCode")
        or "ENG"
    )

    if lang not in allowed_langs:
        continue

    path = channel_data['target']['path']
    epg = channel_data['id']
    name = channel_data['display']['title']

    logo = channel_data['display']['imageUrl'].replace(
        "common,",
        "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/"
    )

    playlist.append(
        f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{epg}" tvg-name="{name}" tvg-logo="{logo}",{epg} {name}'
    )

    encodedpath = urllib.parse.quote_plus(path)

    resp = http.request(
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

    stream = json.loads(resp.data.decode("utf-8"))

    if stream.get('status') == True:
        streamlinks = []
        for j in stream['response']['streams']:
            streamlinks.append(j['url'])

        playlist.append(streamlinks[0] if streamlinks else '')
    else:
        playlist.append('')

# =========================
# SAVE FILE
# =========================
with open('./yupptvfast.m3u', 'w', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')
