import urllib3
import urllib
import json
import time
import re

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

# Function to detect language from channel name
def detect_language_from_name(channel_name):
    channel_name_lower = channel_name.lower()
    
    # Telugu detection
    if any(word in channel_name_lower for word in ['telugu', 'tel', 'zee telugu', 'etv telugu', 'gemini', 'maa', 'star maa']):
        return "TEL", "Telugu"
    
    # Tamil detection
    if any(word in channel_name_lower for word in ['tamil', 'tam', 'sun tv', 'star vijay', 'kalaignar', 'raj tv', 'jaya tv', 'pothigai', 'polimer']):
        return "TAM", "Tamil"
    
    # Malayalam detection
    if any(word in channel_name_lower for word in ['malayalam', 'mal', 'malayalam', 'asianet', 'mazhavil', 'manorama', 'flowers', 'amrita', 'reporter', 'kairali', 'mediaone', 'jaihind']):
        return "MAL", "Malayalam"
    
    # Kannada detection
    if any(word in channel_name_lower for word in ['kannada', 'kan', 'colors kannada', 'star suvarna', 'zee kannada', 'udaya', 'tv9 kannada', 'public tv']):
        return "KAN", "Kannada"
    
    # Hindi detection
    if any(word in channel_name_lower for word in ['hindi', 'hin', 'zee news hindi', 'ndtv india', 'aaj tak', 'zeetv', 'star bharat', 'colors', 'sony', 'sab tv', '&tv', 'news18 india']):
        return "HIN", "Hindi"
    
    # Bengali detection
    if any(word in channel_name_lower for word in ['bengali', 'ben', 'star jalsha', 'zee bengali', 'colors bangla', 'sangeet bangla', 'tv9 bangla', 'republic bangla']):
        return "BEN", "Bengali"
    
    # Marathi detection
    if any(word in channel_name_lower for word in ['marathi', 'mar', 'zee marathi', 'star pravah', 'colors marathi', 'saam tv', 'tv9 marathi', 'abp majha']):
        return "MAR", "Marathi"
    
    # Punjabi detection
    if any(word in channel_name_lower for word in ['punjabi', 'pun', 'zee punjabi', 'ptc', 'chardikla', 'pitara']):
        return "PUN", "Punjabi"
    
    # Gujarati detection
    if any(word in channel_name_lower for word in ['gujarati', 'guj', 'colors gujarati', 'tv9 gujarat', 'zee gujarati']):
        return "GUA", "Gujarati"
    
    # English detection
    if any(word in channel_name_lower for word in ['bbc', 'cnn', 'news18', 'times now', 'republic', 'ndtv 24x7', 'mirror now']):
        return "ENG", "English"
    
    # Default to English if no match found
    return "ENG", "English"

print("Fetching channels and detecting languages...")
channel_counter = 1
processed = 0
language_stats = {}

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
        
        # DETECT LANGUAGE FROM CHANNEL NAME (Primary method)
        lang_code, lang_name = detect_language_from_name(name)
        
        # If API provides language, use it as secondary check
        api_lang = channel_data.get('langCode', '')
        if api_lang and api_lang in language_map:
            api_lang_name = language_map[api_lang]
            # If API says English but name suggests Telugu, trust the name
            if api_lang_name == "English" and lang_name != "English":
                pass  # Keep the name-detected language
            else:
                lang_code = api_lang
                lang_name = api_lang_name
        
        # Special override for known Telugu channels
        telugu_keywords = ['etv', 'gemini', 'maa', 'zee telugu', 'vanitha', 'tv5', 't news', 'ntv', 'hmtv', 'studio n', 'suma news', 'v6 news', 'tv9 telugu', '10 tv', 'i news', 'raj news telugu']
        for keyword in telugu_keywords:
            if keyword in name.lower():
                lang_code = "TEL"
                lang_name = "Telugu"
                break
        
        # Special override for known Tamil channels
        tamil_keywords = ['sun tv', 'star vijay', 'kalaignar', 'raj tv', 'jaya tv', 'pothigai', 'polimer', 'zee tamil', 'colors tamil']
        for keyword in tamil_keywords:
            if keyword in name.lower():
                lang_code = "TAM"
                lang_name = "Tamil"
                break
        
        # Track language statistics
        if lang_name not in language_stats:
            language_stats[lang_name] = 0
        language_stats[lang_name] += 1
        
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
        processed += 1
        if processed % 20 == 0:
            print(f"Processed {processed} channels...")
        
        time.sleep(0.05)  # Small delay to avoid rate limiting
        
    except Exception as e:
        print(f"Error processing channel: {str(e)}")
        continue

# Print language statistics
print("\n" + "="*50)
print("LANGUAGE STATISTICS:")
print("="*50)
for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{lang}: {count} channels")
print("="*50)

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"\n✅ Playlist generated successfully with {processed} channels")
print(f"📁 File saved as: yupptvfast.m3u")
print(f"\n📊 Language breakdown:")
for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"   {lang}: {count} channels")
