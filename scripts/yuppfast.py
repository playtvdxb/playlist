import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# Disable SSL warnings
urllib3.disable_warnings()

# FIXED: Removed display_lang_code=ENG to let API return native language codes
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
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

# Also try without forcing language filter, or keep it as is
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

# Language mapping
language_map = {
    "ENG": "English",
    "HIN": "Hindi",
    "TAM": "Tamil",
    "TEL": "Telugu",
    "MAL": "Malayalam",
    "KAN": "Kannada",
    "BEN": "Bengali",
    "MAR": "Marathi",
    "PUN": "Punjabi",
    "URD": "Urdu",
    "BHO": "Bhojpuri",
    "GUA": "Gujarati",
    "ASS": "Assamese"
}

print("Fetching channels - API should now return native language codes...")
print("="*50)

channel_counter = 1
processed = 0
language_stats = {}
api_lang_stats = {}

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
        
        # NOW use the API's langCode (should be correct after removing display_lang_code)
        lang_code = channel_data.get('langCode', 'ENG')
        lang_name = language_map.get(lang_code, lang_code)
        
        # Track what API is returning
        if lang_name not in api_lang_stats:
            api_lang_stats[lang_name] = 0
        api_lang_stats[lang_name] += 1
        
        # Track final language statistics
        if lang_name not in language_stats:
            language_stats[lang_name] = 0
        language_stats[lang_name] += 1
        
        # Use channel number from API or generate one
        channel_number = channel_data.get('channelNumber', str(channel_counter))
        
        # Create EXTINF line with API's language
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
        processed += 1
        if processed % 20 == 0:
            print(f"Processed {processed} channels...")
        
        time.sleep(0.05)
        
    except Exception as e:
        print(f"Error processing channel: {str(e)}")
        continue

# Print API language statistics
print("\n" + "="*50)
print("API RETURNED LANGUAGE STATISTICS:")
print("="*50)
for lang, count in sorted(api_lang_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{lang}: {count} channels")
print("="*50)
print(f"Total channels processed: {processed}")

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"\n✅ Playlist generated successfully!")
print(f"📁 File saved as: yupptvfast.m3u")
print(f"\n💡 Removed 'display_lang_code=ENG' from token request")
print(f"   API should now return correct language codes!")
