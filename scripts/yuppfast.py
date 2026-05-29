import urllib3
import urllib.parse
import json

playlist = ["#EXTM3U"]

# Disable SSL warnings (not recommended for production, but okay for this script)
urllib3.disable_warnings()

try:
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
        path = i['target']['path']
        epg = i['id']
        name = i['display']['title']
        logo = i['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
        
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
            playlist.append(stream['response']['streams'][0]['url'])
        else:
            playlist.append('# No stream available')

    # Save the playlist
    with open('yupptvfast.m3u', 'w', newline='') as f:
        f.write('\n'.join(playlist))
        
    print(f"Success! Generated playlist with {len(playlist)-1} channels.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
