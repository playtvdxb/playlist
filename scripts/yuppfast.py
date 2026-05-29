import urllib3
import urllib
import json
import time
import re

playlist = ["#EXTM3U"]

# Disable SSL warnings
urllib3.disable_warnings()

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

# ============================================
# LANGUAGE DETECTION (from channel name)
# ============================================
def detect_language(channel_name):
    name_lower = channel_name.lower()
    
    # Tamil channels
    if any(word in name_lower for word in ['tamil', 'polimer', 'puthiya thalaimurai', 'seithigal', 'sun tv', 'star vijay', 'kalaignar', 'raj tv', 'jaya tv', 'pothigai', 'zee tamil', 'colors tamil', 'madha tv', 'moon tv', 'murasu', 'thalaa', 'news tamil', 'puthiya', 'thalaimurai']):
        return "TAM", "Tamil"
    
    # Telugu channels
    if any(word in name_lower for word in ['telugu', 'etv', 'gemini', 'maa', 'zee telugu', 'vanitha', 'tv5', 't news', 'ntv', 'hmtv', 'v6 news', 'tv9 telugu', '10 tv', 'i news', 'sakshi', 'mahaa', 'cvr', 'big tv', 'svbc', 'tolly', 'prime9', 'manatv', 'brk news', 'studio yuva', 'studio one', 'telugu one', 'nkr tv']):
        return "TEL", "Telugu"
    
    # Kannada channels
    if any(word in name_lower for word in ['kannada', 'colors kannada', 'star suvarna', 'zee kannada', 'udaya', 'tv9 kannada', 'public tv', 'tv5 kannada', 'suvarna news', 'republic kannada', 'ayush tv', 'sri sankara kannada']):
        return "KAN", "Kannada"
    
    # Hindi channels
    if any(word in name_lower for word in ['hindi', 'zee news', 'aaj tak', 'ndtv india', 'republic bharat', 'abp news', 'tv9 bharatvarsh', 'good news today', 'sudarshan', 'times now navbharat', 'news18', 'india tv', 'zeetv', 'star bharat', 'colors', 'sony', 'sab tv', '&tv', 'khabar', 'bharat', 'aaj ki khabar', 'c news bharat']):
        return "HIN", "Hindi"
    
    # Bengali channels
    if any(word in name_lower for word in ['bengali', 'star jalsha', 'zee bengali', 'colors bangla', 'tv9 bangla', 'republic bangla', 'kolkata tv', 'abp ananda', '24 ghanta', 'news live bangla', 'rplus', 'calcutta news', 'ctvn']):
        return "BEN", "Bengali"
    
    # Marathi channels
    if any(word in name_lower for word in ['marathi', 'zee marathi', 'star pravah', 'colors marathi', 'tv9 marathi', 'abp majha', 'jai maharashtra', '24 taas', 'fakt marathi', 'saam tv']):
        return "MAR", "Marathi"
    
    # Punjabi channels
    if any(word in name_lower for word in ['punjabi', 'zee punjabi', 'ptc', 'gtc punjabi', 'wah punjabi', 'punjabi hits', 'tabbar hits', 'rozana spokesman', 'wpn', 'pitaara', 'parvasi']):
        return "PUN", "Punjabi"
    
    # Gujarati channels
    if any(word in name_lower for word in ['gujarati', 'tv9 gujarati', 'abp asmita', 'zee 24 kalak', 'gujarat first', 'vtv gujarati', 'mantavya news', 'lakshyatv']):
        return "GUA", "Gujarati"
    
    # Malayalam channels (if any appear)
    if any(word in name_lower for word in ['malayalam', 'asianet', 'mazhavil', 'manorama', 'flowers', 'amrita', 'reporter', 'kairali', 'mediaone']):
        return "MAL", "Malayalam"
    
    # Bhojpuri channels
    if any(word in name_lower for word in ['bhojpuri', 'mahua', 'pasand']):
        return "BHO", "Bhojpuri"
    
    # Assamese channels
    if any(word in name_lower for word in ['assamese', 'nktv', 'rengoni', 'protidin']):
        return "ASS", "Assamese"
    
    # Urdu channels
    if any(word in name_lower for word in ['urdu', 'zee salaam']):
        return "URD", "Urdu"
    
    # English channels (international/news)
    if any(word in name_lower for word in ['bbc', 'cnn', 'wion', 'ndtv 24x7', 'mirror now', 'india today', 'republic tv', 'times now', 'news9', 'willow sports', 'cricket gold', 'voa news', 'oan plus']):
        return "ENG", "English"
    
    # If no language detected, return None
    return None, None

# ============================================
# CATEGORY/GENRE DETECTION (from channel name)
# ============================================
def detect_category(channel_name, api_genre=None):
    name_lower = channel_name.lower()
    
    # Check API genre first (most reliable when available)
    if api_genre:
        api_genre_upper = api_genre.upper()
        if api_genre_upper == 'NEWS':
            return "News"
        elif api_genre_upper == 'SPORTS':
            return "Sports"
        elif api_genre_upper == 'MUSIC':
            return "Music"
        elif api_genre_upper == 'KIDS':
            return "Kids"
        elif api_genre_upper == 'MOVIES':
            return "Movies"
        elif api_genre_upper == 'LIFESTYLE':
            return "Lifestyle"
        elif api_genre_upper == 'EDUCATION':
            return "Education"
        elif api_genre_upper == 'SPIRITUAL':
            return "Spiritual"
        elif api_genre_upper == 'ENTERTAINMENT':
            return "Entertainment"
    
    # Detect from channel name
    if any(word in name_lower for word in ['news', 'times now', 'aaj tak', 'republic', 'ndtv', 'abp', 'tv9', 'india today', 'mirror now', 'wion', 'headlines', 'update', 'khabar', 'samachar', 'express', 'live', 'report', 'bullet']):
        return "News"
    
    if any(word in name_lower for word in ['sports', 'sport', 'cricket', 'football', 'willow', 'espn', 'star sports', 'ten sports', 'fight', 'mma', 'hunt', 'fish', 'nautical', 'yachting', 'adventure', 'pickleball', 'boating', 'fishing', 'chukker', 'chrono', 'itsf', 'xtrem', 'kozoon']):
        return "Sports"
    
    if any(word in name_lower for word in ['music', 'song', 'hits', 'bollywood', 'bhajan', 'devotional', 'sangeet', 'radio', 'balle balle', 'insync', 'haryanvi', 'songdew', 'jupiter', 'wildest wish', 'edgy urban']):
        return "Music"
    
    if any(word in name_lower for word in ['kids', 'cartoon', 'kiddo', 'hooray', 'rhymes', 'green gold', 'pocket films', 'brat tv', 'kartoon']):
        return "Kids"
    
    if any(word in name_lower for word in ['movie', 'films', 'cinema', 'hollywood', 'tolly', 'action', 'drama', 'thriller', 'horror', 'cowboy', 'scifi', 'drive in', 'weshort', 'kung fu', 'bang bang', 'urban action', 'love 2 hate', 'mundo series']):
        return "Movies"
    
    if any(word in name_lower for word in ['spiritual', 'god', 'bhakti', 'temple', 'prayer', 'divya', 'krishna', 'sai', 'bhajan', 'aarti', 'mandir', 'islam', 'christian', 'hosanna', 'angel', 'svbc', 'sharnam', 'brahma kumaris', 'mangalmay', 'disha', 'jinvani', 'astroscience', 'subharti', 'anand', 'peace of mind', 'awakening', 'sana', 'holy god', 'nambikkai', 'sivan temple']):
        return "Spiritual"
    
    if any(word in name_lower for word in ['lifestyle', 'fashion', 'travel', 'food', 'health', 'fitness', 'vanitha', 'beauty', 'home', 'garden', 'cvr health', 'luxury dreams', 'defiance media', 'escape tv']):
        return "Lifestyle"
    
    if any(word in name_lower for word in ['education', 'learning', 'school', 'college', 'university', 'turito', 'iit', 'neet', 'tsat', 'veda', 'knowledge', 'science', 'nipuna', 'vidya', 'english tv']):
        return "Education"
    
    if any(word in name_lower for word in ['comedy', 'lol', 'gags', 'entertainment', 'tv', 'show', 'drama', 'serial', 'ace tv', 'space series', 'unchainedtv', 'voyages', 'trufa', 'nitro tv', 'outer vision', 'awe plus']):
        return "Entertainment"
    
    # Default for non-categorized channels
    return "Others"

print("="*60)
print("FETCHING CHANNELS WITH LANGUAGE + CATEGORY DETECTION")
print("="*60)

channel_counter = 1
processed = 0
language_stats = {}
category_stats = {}
fallback_count = 0

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
        
        # Get genre from channel data if available
        api_genre = channel_data.get('genre', '')
        
        # Detect language from channel name
        lang_code, lang_name = detect_language(name)
        
        # Detect category from channel name and API genre
        category = detect_category(name, api_genre)
        
        # Determine group title based on what was detected
        if lang_code:
            # Language detected - use "Language Category" format
            group_title = f"{lang_name} {category}" if category != "Others" else lang_name
            channel_display = f"{channel_number} {name} [{lang_name} - {category}]"
        else:
            # No language detected - fall back to category only
            group_title = category
            channel_display = f"{channel_number} {name} [{category}]"
            fallback_count += 1
            lang_code = "UNK"
            lang_name = "Unknown"
        
        # Track statistics
        if lang_name not in language_stats:
            language_stats[lang_name] = 0
        language_stats[lang_name] += 1
        
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
        
        # Use channel number
        channel_number = channel_data.get('channelNumber', str(channel_counter))
        
        # Create EXTINF line with language and category
        playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{channel_number}" tvg-name="{name}" tvg-logo="{logo}" tvg-language="{lang_code}" group-title="{group_title}",{channel_number} {name}')
        
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

# Print statistics
print("\n" + "="*60)
print("LANGUAGE DISTRIBUTION:")
print("="*60)
for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{lang}: {count} channels")

print("\n" + "="*60)
print("CATEGORY/GENRE DISTRIBUTION:")
print("="*60)
for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{cat}: {count} channels")
print("="*60)
print(f"Total channels processed: {processed}")
print(f"Channels where language was not detected (used category only): {fallback_count}")

# Write the playlist file
with open('./yupptvfast.m3u', 'w', encoding='utf-8', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

print(f"\n✅ Playlist generated successfully!")
print(f"📁 File saved as: yupptvfast.m3u")
print(f"\n📊 Organization Logic:")
print(f"   - If language detected: group-title = 'Language Category' (e.g., 'Tamil News')")
print(f"   - If language not detected: group-title = Category only (e.g., 'Sports', 'Music')")
print(f"   - Channel format includes both language and category in brackets")
