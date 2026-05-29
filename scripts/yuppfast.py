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

# Complete language mapping
language_map = {
    "ENG": "English",
    "HIN": "Hindi",
    "TAM": "Tamil",
    "TEL": "Telugu",      # Fixed: Now correctly maps to Telugu
    "MAL": "Malayalam",
    "KAN": "Kannada",
    "BEN": "Bengali",
    "MAR": "Marathi",
    "PUN": "Punjabi",
    "URD": "Urdu",
    "BHO": "Bhojpuri",
    "GUA": "Gujarati",
    "ASS": "Assamese",
    "ODI": "Odia",
    "NEP": "Nepali"
}

# Counter for channel numbers
channel_counter = 1

# First, let's debug to see what language codes the API returns
print("Fetching channels...")
debug_sample = []

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
        
        # IMPORTANT: Get the correct language code from API
        # Try multiple possible field names
        lang_code = channel_data.get('langCode') or \
                    channel_data.get('language') or \
                    channel_data.get('languageCode') or \
                    channel_data.get('display', {}).get('langCode') or \
                    "ENG"  # Default to English if not found
        
        # Debug: Print first 10 channels to see language codes
        if len(debug_sample) < 10:
            debug_sample.append({
                'name': name,
                'langCode': channel_data.get('langCode'),
                'language': channel_data.get('language'),
                'languageCode': channel_data.get('languageCode'),
                'display_langCode': channel_data.get('display', {}).get('langCode')
            })
        
        # Map the language code to full name
        lang_name = language_map.get(lang_code.upper(), "English")
        
        # Override based on channel name if needed (safety check)
        name_lower = name.lower()
        if 'telugu' in name_lower or 'tel' in name_lower:
            lang_name = "Telugu"
            lang_code = "TEL"
        elif 'tamil' in name_lower or 'tam' in name_lower:
            lang_name = "Tamil"
            lang_code = "TAM"
        elif 'hindi' in name_lower or 'hin' in name_lower:
            lang_name = "Hindi"
            lang_code = "HIN"
        elif 'malayalam' in name_lower or 'mal' in name_lower:
            lang_name = "Malayalam"
            lang_code = "MAL"
        elif 'kannada' in name_lower or 'kan' in name_lower:
            lang_name = "Kannada"
            lang_code = "KAN"
        elif 'bengali' in name_lower or 'ben' in name_lower:
            lang_name = "Bengali"
            lang_code = "BEN"
        elif 'marathi' in name_lower or 'mar' in name_lower:
            lang_name = "Marathi"
            lang_code = "MAR"
        elif 'punjabi' in name_lower or 'pun' in name_lower:
            lang_name = "Punjabi"
            lang_code = "PUN"
        
        # Use channel number from API or generate one
        channel_number = channel_data.get('channelNumber', str(channel_counter))
        
        # Create the EXTINF line with CORRECT language
        playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{channel_number}" tvg-name="{name}" tvg-logo="{logo}" tvg-language="{lang_code}" group-title="{lang_name}",{channel_number} {name}')
        
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

# Print debug info
print("\n=== DEBUG: First 10 channels language codes ===")
for item in debug_sample:
    print(f"Channel: {item['name']}")
    print(f"  langCode: {item['langCode']}")
    print(f"  language: {item['language']}")
    print(f"  languageCode: {item['languageCode']}")
    print(f"  display.langCode: {item['display_langCode']}")
    print("---")

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"\nPlaylist generated successfully with {channel_counter - 1} channels")
print("Check yupptvfast.m3u for language fixes")
