import urllib3
import urllib.parse
import json
import sys

urllib3.disable_warnings()
playlist = ["#EXTM3U"]

try:
    # Get token
    http = urllib3.PoolManager()
    resp = http.request(
        "GET",
        "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
        headers={
            "Accept": "application/json",
            "Tenant-Code": "yuppfast",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    if resp.status != 200:
        print(f"Token request failed: {resp.status}")
        sys.exit(1)
        
    data = resp.json()
    sessionid = data['response']['sessionId']
    
    # Get channels
    resp = http.request(
        "GET",
        "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
        headers={
            "Accept": "application/json",
            "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
            "Tenant-Code": "yuppfast",
            "Session-Id": sessionid,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    if resp.status != 200:
        print(f"Channels request failed: {resp.status}")
        sys.exit(1)
        
    channels = resp.json()
    
    # Process each channel
    for channel in channels['response']['data']:
        try:
            path = channel['target']['path']
            epg = channel['id']
            name = channel['display']['title']
            logo = channel['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
            
            playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-name="{name}" tvg-logo="{logo}",{name}')
            
            # Get stream URL
            encodedpath = urllib.parse.quote_plus(path)
            resp = http.request(
                "GET",
                f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
                headers={
                    "Accept": "application/json",
                    "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
                    "Tenant-Code": "yuppfast",
                    "Session-Id": sessionid,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            stream = resp.json()
            
            if stream.get('status') and stream.get('response', {}).get('streams'):
                playlist.append(stream['response']['streams'][0]['url'])
            else:
                playlist.append('')
                
        except Exception as e:
            print(f"Error processing channel {channel.get('id', 'unknown')}: {e}")
            playlist.append('')
            continue
    
    # Save file
    with open('yupptvfast.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(playlist))
    
    print(f"Success! Created playlist with {len(playlist)-1} channels")
    
except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)
