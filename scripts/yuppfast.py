import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# Disable SSL warnings if needed
urllib3.disable_warnings()

resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
)

jsonresp = resp.json()
sessionid = jsonresp['response']['sessionId']

resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
)

jsonresp = resp.json()

# Language mapping to match your CHANNELS categories
language_map = {
    "ENG": "English",
    "HIN": "Hindi",
    "TAM": "Tamil",
    "MAR": "Marathi",
    "BEN": "Bengali",
    "TEL": "Telugu",
    "KAN": "Kannada",
    "BHO": "Bhojpuri",
    "GUA": "Gujarati",
    "PUN": "Punjabi",
    "ASS": "Assamese",
    "URD": "Urdu",
    "MAL": "Malayalam"  # Added for Malayalam
}

# Counter for channel numbers
channel_counter = 1

for i in jsonresp['response']['data']:
    try:
        stringdata = json.dumps(i, indent=4)
        channel_data = json.loads(stringdata)
        
        # Extract channel information
        path = channel_data.get('target', {}).get('path', '')
        if not path:
            continue
            
        epg = channel_data.get('id', '')
        name = channel_data.get('display', {}).get('title', 'Unknown')
        logo = channel_data.get('display', {}).get('imageUrl', '').replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
        
        # Get language code and name
        lang_code = channel_data.get('langCode', 'ENG')
        lang_name = language_map.get(lang_code, lang_code)
        
        # Create a clean channel ID (remove spaces and special characters)
        channel_id = f"yupp_{epg}".lower()
        channel_id = ''.join(c if c.isalnum() or c == '_' else '_' for c in channel_id)
        
        # Use channel number from API or generate one
        channel_number = channel_data.get('channelNumber', str(channel_counter))
        
        # Create the EXTINF line compatible with your script
        # Format: tvg-id (for EPG), tvg-chno (channel number), group-title (category/language)
        playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{channel_number}" tvg-name="{name}" tvg-logo="{logo}" group-title="{lang_name}",{channel_number} {name}')
        
        # Get stream URL
        encodedpath = urllib.parse.quote_plus(path)
        resp = urllib3.request(
            "GET",
            f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
                "Tenant-Code": "yuppfast",
                "Origin": "https://www.yupptv.com",
                "Referer": "https://www.yupptv.com/",
                "Session-Id": sessionid,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
            }
        )
        
        stream = resp.json()
        if stream.get('status') == True:
            streams = stream.get('response', {}).get('streams', [])
            if streams:
                stream_url = streams[0].get('url', '')
                playlist.append(stream_url)
            else:
                playlist.append('')
        else:
            playlist.append('')
        
        channel_counter += 1
        time.sleep(0.1)  # Small delay to avoid rate limiting
        
    except Exception as e:
        print(f"Error processing channel: {str(e)}")
        continue

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"Playlist generated successfully with {channel_counter - 1} channels")
