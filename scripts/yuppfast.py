import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# Disable SSL warnings
urllib3.disable_warnings()

try:
    print("Step 1: Getting token...")
    resp = urllib3.request(
        "GET",
        "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Tenant-Code": "yuppfast",
            "Origin": "https://www.yupptv.com",
            "Referer": "https://www.yupptv.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Connection": "close"
        },
        timeout=30
    )
    
    if resp.status != 200:
        print(f"Token request failed with status: {resp.status}")
        exit(1)
        
    jsonresp = resp.json()
    sessionid = jsonresp.get('response', {}).get('sessionId')
    
    if not sessionid:
        print("Failed to get session ID")
        exit(1)
    
    print(f"Token obtained. Session ID: {sessionid[:20]}...")
    
except Exception as e:
    print(f"Error getting token: {str(e)}")
    exit(1)

try:
    print("\nStep 2: Fetching channels...")
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Connection": "close"
        },
        timeout=30
    )
    
    if resp.status != 200:
        print(f"Channels request failed with status: {resp.status}")
        exit(1)
        
    jsonresp = resp.json()
    channels = jsonresp.get('response', {}).get('data', [])
    
    if not channels:
        print("No channels received from API")
        exit(1)
    
    print(f"Found {len(channels)} channels")
    
except Exception as e:
    print(f"Error fetching channels: {str(e)}")
    exit(1)

# ============================================
# LANGUAGE DETECTION
# ============================================
def detect_language(channel_name):
    name_lower = channel_name.lower()
    
    if any(word in name_lower for word in ['tamil', 'polimer', 'puthiya thalaimurai', 'seithigal', 'sun tv', 'star vijay', 'kalaignar', 'raj tv', 'jaya tv', 'pothigai', 'zee tamil', 'colors tamil', 'madha tv', 'moon tv', 'murasu', 'news tamil']):
        return "TAM", "Tamil"
    
    if any(word in name_lower for word in ['telugu', 'etv', 'gemini', 'maa', 'zee telugu', 'vanitha', 'tv5', 't news', 'ntv', 'hmtv', 'v6 news', 'tv9 telugu', '10 tv', 'i news', 'sakshi', 'mahaa', 'cvr', 'big tv', 'svbc', 'tolly', 'prime9', 'manatv']):
        return "TEL", "Telugu"
    
    if any(word in name_lower for word in ['kannada', 'colors kannada', 'star suvarna', 'zee kannada', 'udaya', 'tv9 kannada', 'public tv', 'tv5 kannada']):
        return "KAN", "Kannada"
    
    if any(word in name_lower for word in ['hindi', 'zee news', 'aaj tak', 'ndtv india', 'republic bharat', 'abp news', 'tv9 bharatvarsh', 'good news today', 'sudarshan', 'times now navbharat']):
        return "HIN", "Hindi"
    
    if any(word in name_lower for word in ['bengali', 'star jalsha', 'zee bengali', 'tv9 bangla', 'republic bangla', 'kolkata tv', 'abp ananda', '24 ghanta']):
        return "BEN", "Bengali"
    
    if any(word in name_lower for word in ['marathi', 'zee marathi', 'star pravah', 'tv9 marathi', 'abp majha', 'jai maharashtra', '24 taas']):
        return "MAR", "Marathi"
    
    if any(word in name_lower for word in ['punjabi', 'zee punjabi', 'ptc', 'gtc punjabi', 'wah punjabi']):
        return "PUN", "Punjabi"
    
    if any(word in name_lower for word in ['gujarati', 'tv9 gujarati', 'abp asmita', 'zee 24 kalak', 'gujarat first']):
        return "GUA", "Gujarati"
    
    return "ENG", "English"

# ============================================
# CATEGORY DETECTION
# ============================================
def detect_category(channel_name):
    name_lower = channel_name.lower()
    
    if any(word in name_lower for word in ['news', 'times now', 'aaj tak', 'republic', 'ndtv', 'abp', 'tv9', 'india today', 'mirror now', 'wion']):
        return "News"
    
    if any(word in name_lower for word in ['sports', 'sport', 'cricket', 'willow', 'espn', 'star sports', 'fight', 'mma', 'hunt', 'fish', 'nautical', 'yachting', 'adventure']):
        return "Sports"
    
    if any(word in name_lower for word in ['music', 'song', 'hits', 'bollywood', 'bhajan', 'devotional', 'sangeet', 'radio', 'balle balle']):
        return "Music"
    
    if any(word in name_lower for word in ['kids', 'cartoon', 'kiddo', 'hooray', 'rhymes', 'green gold']):
        return "Kids"
    
    if any(word in name_lower for word in ['movie', 'films', 'cinema', 'hollywood', 'tolly', 'action', 'drama', 'thriller', 'horror']):
        return "Movies"
    
    if any(word in name_lower for word in ['spiritual', 'god', 'bhakti', 'temple', 'prayer', 'divya', 'krishna', 'sai', 'svbc', 'angel', 'hosanna']):
        return "Spiritual"
    
    if any(word in name_lower for word in ['lifestyle', 'fashion', 'travel', 'food', 'health', 'fitness', 'vanitha']):
        return "Lifestyle"
    
    if any(word in name_lower for word in ['education', 'learning', 'school', 'college', 'turito', 'iit', 'neet', 'tsat']):
        return "Education"
    
    return "Entertainment"

print("\nStep 3: Processing channels...")
print("="*60)

channel_counter = 1
processed = 0
failed = 0

for channel in channels:
    try:
        # Extract channel information
        path = channel.get('target', {}).get('path', '')
        if not path:
            continue
            
        epg = channel.get('id', '')
        name = channel.get('display', {}).get('title', 'Unknown')
        logo = channel.get('display', {}).get('imageUrl', '').replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
        
        # Detect language and category
        lang_code, lang_name = detect_language(name)
        category = detect_category(name)
        
        # Create group title
        group_title = f"{lang_name} {category}" if lang_name != "English" else category
        
        # Add EXTINF line
        playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{channel_counter}" tvg-name="{name}" tvg-logo="{logo}" tvg-language="{lang_code}" group-title="{group_title}",{channel_counter} {name}')
        
        # Get stream URL
        encodedpath = urllib.parse.quote_plus(path)
        
        try:
            stream_resp = urllib3.request(
                "GET",
                f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
                    "Tenant-Code": "yuppfast",
                    "Session-Id": sessionid,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                timeout=15
            )
            
            if stream_resp.status == 200:
                stream_data = stream_resp.json()
                if stream_data.get('status') == True:
                    streams = stream_data.get('response', {}).get('streams', [])
                    if streams and streams[0].get('url'):
                        playlist.append(streams[0]['url'])
                    else:
                        playlist.append('')
                        failed += 1
                else:
                    playlist.append('')
                    failed += 1
            else:
                playlist.append('')
                failed += 1
                
        except Exception as e:
            print(f"  Stream error for {name}: {str(e)[:50]}")
            playlist.append('')
            failed += 1
        
        processed += 1
        channel_counter += 1
        
        if processed % 10 == 0:
            print(f"  Processed {processed} channels...")
        
        time.sleep(0.1)  # Small delay to avoid rate limiting
        
    except Exception as e:
        print(f"Error processing channel: {str(e)[:100]}")
        failed += 1
        continue

# Write the playlist file
print("\nStep 4: Saving playlist...")
with open('./yupptvfast.m3u', 'w', encoding='utf-8') as f:
    for line in playlist:
        f.write(f'{line}\n')

print("="*60)
print(f"✅ Playlist generated successfully!")
print(f"📁 File saved as: yupptvfast.m3u")
print(f"📊 Statistics:")
print(f"   Total channels in playlist: {processed}")
print(f"   Channels with stream URLs: {processed - failed}")
print(f"   Channels without streams: {failed}")
print("="*60)
