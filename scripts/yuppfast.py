import urllib3
import urllib
import json
import time

playlist = ["#EXTM3U"]

# REMOVED: &display_lang_code=ENG from the URL below
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

def get_language(name):
    name_lower = name.lower()
    if any(word in name_lower for word in ['tamil', 'polimer', 'puthiya', 'seithigal', 'sun tv', 'star vijay']):
        return "Tamil"
    if any(word in name_lower for word in ['telugu', 'etv', 'gemini', 'maa', 'vanitha', 'tv5', 'ntv', 'hmtv', 'v6 news', 'tv9 telugu']):
        return "Telugu"
    if any(word in name_lower for word in ['kannada', 'tv9 kannada', 'suvarna']):
        return "Kannada"
    if any(word in name_lower for word in ['hindi', 'zee news', 'aaj tak', 'ndtv', 'republic bharat', 'abp news']):
        return "Hindi"
    if any(word in name_lower for word in ['bengali', 'star jalsha', 'zee bengali', 'tv9 bangla']):
        return "Bengali"
    if any(word in name_lower for word in ['marathi', 'zee marathi', 'star pravah', 'tv9 marathi', 'abp majha']):
        return "Marathi"
    if any(word in name_lower for word in ['punjabi', 'zee punjabi', 'ptc', 'gtc punjabi']):
        return "Punjabi"
    if any(word in name_lower for word in ['gujarati', 'tv9 gujarati', 'abp asmita']):
        return "Gujarati"
    return "English"

def get_category(name):
    name_lower = name.lower()
    if any(word in name_lower for word in ['news', 'times now', 'aaj tak', 'republic', 'ndtv', 'abp', 'tv9', 'india today']):
        return "News"
    if any(word in name_lower for word in ['sports', 'sport', 'cricket', 'willow', 'fight', 'mma']):
        return "Sports"
    if any(word in name_lower for word in ['music', 'song', 'hits', 'bollywood']):
        return "Music"
    if any(word in name_lower for word in ['kids', 'cartoon', 'kiddo']):
        return "Kids"
    if any(word in name_lower for word in ['movie', 'action', 'drama', 'thriller', 'horror']):
        return "Movies"
    if any(word in name_lower for word in ['spiritual', 'god', 'bhakti', 'svbc', 'angel']):
        return "Spiritual"
    return "Entertainment"

for i in jsonresp['response']['data']:
    stringdata = json.dumps(i, indent=4)
    channel_data = json.loads(stringdata)
    path = channel_data['target']['path']
    epg = channel_data['id']
    name = channel_data['display']['title']
    logo = channel_data['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
    
    language = get_language(name)
    category = get_category(name)
    
    if language == "English":
        group_title = category
    else:
        group_title = f"{language} {category}"
    
    playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{epg}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group_title}",{epg} {name}')
    
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
    if stream['status'] == True:
        for j in stream['response']['streams']:
            streamlinks = []
            streamlinks.append(j['url'])
        playlist.append(streamlinks[0])
    else:
        playlist.append('')

with open('./yupptvfast.m3u', 'w', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

f.close()
