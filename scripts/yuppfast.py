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

# FIXED: Added MAL (Malayalam) to the language filter
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,MAL,BHO,GUA,PUN,ASS,URD",
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

# Language mapping with Malayalam
language_map = {
    "ENG": "English",
    "HIN": "Hindi",
    "TAM": "Tamil",
    "TEL": "Telugu",
    "MAL": "Malayalam",  # Added Malayalam
    "KAN": "Kannada",
    "BEN": "Bengali",
    "MAR": "Marathi",
    "PUN": "Punjabi",
    "URD": "Urdu",
    "BHO": "Bhojpuri",
    "GUA": "Gujarati",
    "ASS": "Assamese"
}

# Comprehensive language detection function
def detect_language(channel_name):
    name_lower = channel_name.lower()
    
    # Malayalam detection (HIGHEST PRIORITY - added many keywords)
    malayalam_keywords = [
        'malayalam', 'mal', 'asianet', 'mazhavil', 'manorama', 'flowers', 'amrita', 
        'reporter', 'kairali', 'mediaone', 'jaihind', 'janam', 'kaumudy', 'shalom', 
        'mangalam', 'mathrubhumi', 'news18 malayalam', 'zee keralam', 'surya tv',
        'kerala vision', 'darshana tv', 'harvest tv', 'goodness tv', 'power vision'
    ]
    for keyword in malayalam_keywords:
        if keyword in name_lower:
            return "MAL", "Malayalam"
    
    # Telugu detection
    telugu_keywords = [
        'telugu', 'etv', 'gemini', 'maa', 'zee telugu', 'vanitha', 'tv5', 't news', 
        'ntv', 'hmtv', 'studio n', 'suma news', 'v6 news', 'tv9 telugu', '10 tv', 
        'i news', 'raj news telugu', 'sakshi', 'mahaa', 'cvr', 'big tv', 'bhakti tv',
        'svbc', 'tolly', 'telugu one', 'prime9', 'manatv', 'tsat', 'brk news'
    ]
    for keyword in telugu_keywords:
        if keyword in name_lower:
            return "TEL", "Telugu"
    
    # Tamil detection
    tamil_keywords = [
        'tamil', 'sun tv', 'star vijay', 'kalaignar', 'raj tv', 'jaya tv', 'pothigai', 
        'polimer', 'zee tamil', 'colors tamil', 'news tamil', 'puthiya thalaimurai',
        'seithigal', 'madha tv', 'sivan temple', 'nambikkai', 'athavan', 'moon tv',
        'peppers tv', 'ibc radio', 'murasu', 'thalaa'
    ]
    for keyword in tamil_keywords:
        if keyword in name_lower:
            return "TAM", "Tamil"
    
    # Kannada detection
    kannada_keywords = [
        'kannada', 'colors kannada', 'star suvarna', 'zee kannada', 'udaya', 'tv9 kannada',
        'public tv', 'news18 kannada', 'kasthuri', 'tv5 kannada', 'suvarna news'
    ]
    for keyword in kannada_keywords:
        if keyword in name_lower:
            return "KAN", "Kannada"
    
    # Hindi detection
    hindi_keywords = [
        'hindi', 'zee news', 'aaj tak', 'ndtv india', 'republic bharat', 'news18', 
        'abp news', 'tv9 bharatvarsh', 'times now navbharat', 'good news today',
        'zeetv', 'star bharat', 'colors', 'sony', 'sab tv', '&tv', 'india tv',
        'sudarshan news', 'khabar', 'bharat', 'aaj ki khabar', 'c news bharat'
    ]
    for keyword in hindi_keywords:
        if keyword in name_lower:
            return "HIN", "Hindi"
    
    # Bengali detection
    bengali_keywords = [
        'bengali', 'star jalsha', 'zee bengali', 'colors bangla', 'sangeet bangla', 
        'tv9 bangla', 'republic bangla', 'news live bangla', 'kolkata tv', 'rplus',
        'abp ananda', '24 ghanta', 'calcuttanews', 'ctvn'
    ]
    for keyword in bengali_keywords:
        if keyword in name_lower:
            return "BEN", "Bengali"
    
    # Marathi detection
    marathi_keywords = [
        'marathi', 'zee marathi', 'star pravah', 'colors marathi', 'saam tv', 
        'tv9 marathi', 'abp majha', 'jai maharashtra', '24 taas', 'fakt marathi'
    ]
    for keyword in marathi_keywords:
        if keyword in name_lower:
            return "MAR", "Marathi"
    
    # Punjabi detection
    punjabi_keywords = [
        'punjabi', 'zee punjabi', 'ptc', 'chardikla', 'pitara', 'gtc punjabi',
        'punjabi hits', 'tabbar hits', 'wpn', 'rozana spokesman', 'wah punjabi'
    ]
    for keyword in punjabi_keywords:
        if keyword in name_lower:
            return "PUN", "Punjabi"
    
    # Gujarati detection
    gujarati_keywords = [
        'gujarati', 'colors gujarati', 'tv9 gujarati', 'zee gujarati', 'abp asmita',
        'zee 24 kalak', 'mantavya news', 'vtv gujarati', 'gujarat first'
    ]
    for keyword in gujarati_keywords:
        if keyword in name_lower:
            return "GUA", "Gujarati"
    
    # Bhojpuri detection
    bhojpuri_keywords = ['bhojpuri', 'mahua', 'pasand']
    for keyword in bhojpuri_keywords:
        if keyword in name_lower:
            return "BHO", "Bhojpuri"
    
    # Assamese detection
    assamese_keywords = ['assamese', 'nktv', 'rengoni', 'protidin']
    for keyword in assamese_keywords:
        if keyword in name_lower:
            return "ASS", "Assamese"
    
    # Urdu detection
    urdu_keywords = ['urdu', 'zee salaam', 'etv urdu']
    for keyword in urdu_keywords:
        if keyword in name_lower:
            return "URD", "Urdu"
    
    # Default to English for international/news channels
    english_keywords = ['bbc', 'cnn', 'wion', 'ndtv', 'mirror now', 'india today', 
                        'republic tv', 'times now', 'news9', 'willow sports']
    for keyword in english_keywords:
        if keyword in name_lower:
            return "ENG", "English"
    
    # If no match, return None (will use API value)
    return None, None

print("Fetching channels and detecting languages...")
channel_counter = 1
processed = 0
language_stats = {}
corrected_count = 0

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
        
        # Get API language
        api_lang_code = channel_data.get('langCode', 'ENG')
        api_lang_name = language_map.get(api_lang_code, "English")
        
        # Detect language from channel name
        detected_lang_code, detected_lang_name = detect_language(name)
        
        # Use detected language if found, otherwise use API language
        if detected_lang_code:
            lang_code = detected_lang_code
            lang_name = detected_lang_name
            if api_lang_name != detected_lang_name:
                corrected_count += 1
        else:
            lang_code = api_lang_code
            lang_name = api_lang_name
        
        # Track language statistics
        if lang_name not in language_stats:
            language_stats[lang_name] = 0
        language_stats[lang_name] += 1
        
        # Use channel number from API or generate one
        channel_number = channel_data.get('channelNumber', str(channel_counter))
        
        # Create the EXTINF line
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

# Print language statistics
print("\n" + "="*50)
print("LANGUAGE STATISTICS:")
print("="*50)
for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{lang}: {count} channels")
print("="*50)
print(f"Channels corrected from API default: {corrected_count}")
print(f"Total channels processed: {processed}")

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"\n✅ Playlist generated successfully!")
print(f"📁 File saved as: yupptvfast.m3u")
print(f"\n💡 Note: Added MAL (Malayalam) to language filter")
