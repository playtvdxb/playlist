import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# Disable SSL warnings
urllib3.disable_warnings()

print("Step 1: Getting token...")
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

jsonresp = resp.json()
sessionid = jsonresp['response']['sessionId']
print(f"Session ID: {sessionid[:30]}...")

print("\nStep 2: Fetching channels...")
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

jsonresp = resp.json()
channels = jsonresp.get('response', {}).get('data', [])
print(f"Found {len(channels)} channels")

# Language detection function
def detect_language(channel_name):
    name_lower = channel_name.lower()
    
    if any(word in name_lower for word in ['tamil', 'polimer', 'puthiya thalaimurai', 'seithigal']):
        return "TAM", "Tamil"
    if any(word in name_lower for word in ['telugu', 'etv', 'gemini', 'maa', 'vanitha', 'tv5', 'ntv', 'hmtv']):
        return "TEL", "Telugu"
    if any(word in name_lower for word in ['kannada', 'tv9 kannada', 'suvarna']):
        return "KAN", "Kannada"
    if any(word in name_lower for word in ['hindi', 'zee news', 'aaj tak', 'ndtv', 'republic bharat']):
        return "HIN", "Hindi"
    if any(word in name_lower for word in ['bengali', 'star jalsha', 'zee bengali']):
        return "BEN", "Bengali"
    if any(word in name_lower for word in ['marathi', 'zee marathi', 'abp majha']):
        return "MAR", "Marathi"
    if any(word in name_lower for word in ['punjabi', 'zee punjabi', 'ptc']):
        return "PUN", "Punjabi"
    if any(word in name_lower for word in ['gujarati', 'tv9 gujarati', 'abp asmita']):
        return "GUA", "Gujarati"
    
    return "ENG", "English"

# Category detection function
def detect_category(channel_name):
    name_lower = channel_name.lower()
    
    if any(word in name_lower for word in ['news', 'times now', 'aaj tak', 'republic', 'ndtv', 'abp']):
        return "News"
    if any(word in name_lower for word in ['sports', 'sport', 'cricket', 'willow', 'fight', 'mma']):
        return "Sports"
    if any(word in name_lower for word in ['music', 'song', 'hits', 'bollywood']):
        return "Music"
    if any(word in name_lower for word in ['kids', 'cartoon', 'kiddo']):
        return "Kids"
    if any(word in name_lower for word in ['movie', 'films', 'cinema', 'action', 'drama']):
        return "Movies"
    if any(word in name_lower for word in ['spiritual', 'god', 'bhakti', 'temple', 'svbc']):
        return "Spiritual"
    if any(word in name_lower for word in ['lifestyle', 'fashion', 'travel', 'health']):
        return "Lifestyle"
    if any(word in name_lower for word in ['education', 'learning', 'turito']):
        return "Education"
    
    return "Entertainment"

print("\nStep 3: Fetching stream URLs...")
print("="*60)

success_count = 0
failed_count = 0

for idx, channel in enumerate(channels[:50], 1):  # Process first 50 channels for testing
    try:
        # Get channel path
        path = channel.get('target', {}).get('path', '')
        if not path:
            print(f"  {idx}. No path found for channel {channel.get('id', 'Unknown')}")
            continue
            
        name = channel.get('display', {}).get('title', 'Unknown')
        epg = channel.get('id', '')
        logo = channel.get('display', {}).get('imageUrl', '').replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
        
        # Get language and category
        lang_code, lang_name = detect_language(name)
        category = detect_category(name)
        group_title = f"{lang_name} {category}" if lang_name != "English" else category
        
        # Add EXTINF line
        playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{idx}" tvg-name="{name}" tvg-logo="{logo}" tvg-language="{lang_code}" group-title="{group_title}",{idx} {name}')
        
        # Fetch stream URL
        encodedpath = urllib.parse.quote_plus(path)
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
            timeout=10
        )
        
        if stream_resp.status == 200:
            stream_data = stream_resp.json()
            print(f"  {idx}. {name[:30]} - API Response: {stream_data.get('status')}")
            
            if stream_data.get('status') == True:
                streams = stream_data.get('response', {}).get('streams', [])
                if streams and streams[0].get('url'):
                    stream_url = streams[0]['url']
                    playlist.append(stream_url)
                    success_count += 1
                    print(f"      ✓ Got stream URL")
                else:
                    playlist.append('# No stream URL found')
                    failed_count += 1
                    print(f"      ✗ No stream URL in response")
            else:
                playlist.append('# Stream API returned false')
                failed_count += 1
                print(f"      ✗ API returned status false")
        else:
            playlist.append(f'# HTTP {stream_resp.status} error')
            failed_count += 1
            print(f"      ✗ HTTP {stream_resp.status}")
        
        time.sleep(0.1)
        
    except Exception as e:
        print(f"  {idx}. Error: {str(e)[:80]}")
        playlist.append(f'# Error: {str(e)[:50]}')
        failed_count += 1
        continue

print("\n" + "="*60)
print(f"RESULTS:")
print(f"  Successfully fetched streams: {success_count}")
print(f"  Failed to fetch streams: {failed_count}")
print(f"  Total channels processed: {success_count + failed_count}")

# Save the playlist
with open('./yupptvfast.m3u', 'w', encoding='utf-8') as f:
    for line in playlist:
        f.write(f'{line}\n')

print(f"\n✅ Playlist saved as: yupptvfast.m3u")
print(f"📊 Check the file - stream URLs are now included")
