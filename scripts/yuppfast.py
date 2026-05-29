import urllib3
import urllib
import json

playlist = ["#EXTM3U"]

# YOUR WORKER URL
WORKER_URL = "https://binsip.tvlive.workers.dev"

urllib3.disable_warnings()

# Get token
resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
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
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

jsonresp = resp.json()

def get_language(name):
    n = name.lower()
    if any(w in n for w in ['tamil', 'polimer', 'puthiya', 'seithigal', 'sun tv', 'star vijay']): return "Tamil"
    if any(w in n for w in ['telugu', 'etv', 'gemini', 'maa', 'vanitha', 'tv5', 'ntv', 'hmtv', 'v6 news', 'tv9 telugu']): return "Telugu"
    if any(w in n for w in ['kannada', 'tv9 kannada', 'suvarna']): return "Kannada"
    if any(w in n for w in ['hindi', 'zee news', 'aaj tak', 'ndtv', 'republic bharat', 'abp news']): return "Hindi"
    if any(w in n for w in ['bengali', 'star jalsha', 'zee bengali', 'tv9 bangla']): return "Bengali"
    if any(w in n for w in ['marathi', 'zee marathi', 'star pravah', 'tv9 marathi', 'abp majha']): return "Marathi"
    if any(w in n for w in ['punjabi', 'zee punjabi', 'ptc', 'gtc punjabi']): return "Punjabi"
    if any(w in n for w in ['gujarati', 'tv9 gujarati', 'abp asmita']): return "Gujarati"
    return "English"

def get_category(name):
    n = name.lower()
    if any(w in n for w in ['news', 'times now', 'aaj tak', 'republic', 'ndtv', 'abp', 'tv9', 'india today']): return "News"
    if any(w in n for w in ['sports', 'sport', 'cricket', 'willow', 'fight', 'mma']): return "Sports"
    if any(w in n for w in ['music', 'song', 'hits', 'bollywood']): return "Music"
    if any(w in n for w in ['kids', 'cartoon', 'kiddo']): return "Kids"
    if any(w in n for w in ['movie', 'action', 'drama', 'thriller', 'horror']): return "Movies"
    if any(w in n for w in ['spiritual', 'god', 'bhakti', 'svbc', 'angel']): return "Spiritual"
    return "Entertainment"

# Process channels
for i in jsonresp['response']['data']:
    path = i['target']['path']
    epg = i['id']
    name = i['display']['title']
    logo = i['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
    
    language = get_language(name)
    category = get_category(name)
    group_title = category if language == "English" else f"{language} {category}"
    
    playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{epg}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group_title}",{epg} {name}')
    
    # Get stream URL from API
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    stream = resp.json()
    
    if stream['status'] == True and stream['response']['streams']:
        direct_url = stream['response']['streams'][0]['url']
        # ⭐ KEY CHANGE: Route through worker to handle token refresh
        playlist.append(f"{WORKER_URL}/api/refresh?url={urllib.parse.quote(direct_url)}")
    else:
        playlist.append('')

# Save playlist
with open('./yupptvfast.m3u', 'w', newline='') as f:
    f.write('\n'.join(playlist))

print(f"✅ Playlist generated with {len(playlist)//2} channels")
print(f"📁 All streams routed through: {WORKER_URL}")
