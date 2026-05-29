import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# Get session token
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

jsonresp = resp.json()
sessionid = jsonresp['response']['sessionId']

# Get channels
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

jsonresp = resp.json()

# Process each channel
for i in jsonresp['response']['data']:
    channel_data = i  # No need for json.dumps/loads
    path = channel_data['target']['path']
    epg = channel_data['id']
    name = channel_data['display']['title']
    logo = channel_data['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
    
    playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}')
    
    encodedpath = urllib.parse.quote_plus(path)
    resp = urllib3.request(
        "GET",
        f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
            "Tenant-Code": "yuppfast",
            "Origin": "https://www.yupptv.com",
            "Session-Id": sessionid,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    stream = resp.json()
    if stream['status'] == True:
        stream_url = stream['response']['streams'][0]['url']  # Simplified
        playlist.append(stream_url)
    else:
        playlist.append('')

# Save the playlist
with open('yupptvfast.m3u', 'w', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')
