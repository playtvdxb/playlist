import urllib3
import urllib
import json

http = urllib3.PoolManager()

playlist = ["#EXTM3U"]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Tenant-Code": "yuppfast",
    "Origin": "https://www.yupptv.com",
    "Referer": "https://www.yupptv.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

# ============================================
# GET TOKEN
# ============================================

token_url = (
    "https://yuppfast-api.revlet.net/service/api/v1/get/token"
    "?tenant_code=yuppfast"
    "&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c"
    "&product=yuppfast"
    "&device_id=5"
    "&device_sub_type=Chrome,145.0.0.0,Windows"
    "&client_app_version=1"
    "&timezone=Asia/Calcutta"
)

resp = http.request(
    "GET",
    token_url,
    headers=HEADERS
)

jsonresp = json.loads(resp.data.decode("utf-8"))

sessionid = jsonresp['response']['sessionId']

# ============================================
# CHANNEL LIST
# ============================================

channel_headers = HEADERS.copy()

channel_headers.update({
    "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
    "Session-Id": sessionid
})

channels_url = (
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels"
    "?filter=genreCode:all;"
    "langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD"
)

resp = http.request(
    "GET",
    channels_url,
    headers=channel_headers
)

jsonresp = json.loads(resp.data.decode("utf-8"))

# ============================================
# LANGUAGE DETECTION
# ============================================

def get_language(name):

    name_lower = name.lower()

    if any(word in name_lower for word in [
        'tamil', 'sun tv', 'vijay',
        'polimer', 'puthiya'
    ]):
        return "Tamil"

    if any(word in name_lower for word in [
        'telugu', 'gemini', 'maa',
        'etv', 'tv9 telugu'
    ]):
        return "Telugu"

    if any(word in name_lower for word in [
        'kannada', 'suvarna'
    ]):
        return "Kannada"

    if any(word in name_lower for word in [
        'hindi', 'aaj tak',
        'republic bharat'
    ]):
        return "Hindi"

    if any(word in name_lower for word in [
        'bengali', 'jalsha'
    ]):
        return "Bengali"

    if any(word in name_lower for word in [
        'marathi', 'pravah'
    ]):
        return "Marathi"

    if any(word in name_lower for word in [
        'punjabi', 'ptc'
    ]):
        return "Punjabi"

    if any(word in name_lower for word in [
        'gujarati', 'asmita'
    ]):
        return "Gujarati"

    return "English"

# ============================================
# CATEGORY DETECTION
# ============================================

def get_category(name):

    name_lower = name.lower()

    if any(word in name_lower for word in [
        'news', 'aaj tak', 'ndtv',
        'republic', 'abp', 'tv9'
    ]):
        return "News"

    if any(word in name_lower for word in [
        'sports', 'cricket',
        'willow', 'mma'
    ]):
        return "Sports"

    if any(word in name_lower for word in [
        'music', 'hits'
    ]):
        return "Music"

    if any(word in name_lower for word in [
        'kids', 'cartoon'
    ]):
        return "Kids"

    if any(word in name_lower for word in [
        'movie', 'cinema', 'films'
    ]):
        return "Movies"

    if any(word in name_lower for word in [
        'bhakti', 'spiritual',
        'god', 'svbc'
    ]):
        return "Spiritual"

    return "Entertainment"

# ============================================
# GET BEST STREAM
# ============================================

def get_best_stream(streams):

    if not streams:
        return ""

    best_stream = None
    best_score = -1

    for s in streams:

        url = s.get('url', '')

        if not url:
            continue

        score = 0

        lower = url.lower()

        # QUALITY DETECTION
        if '1080' in lower:
            score += 500

        elif '720' in lower:
            score += 300

        elif '480' in lower:
            score += 100

        # PREFER HLS
        if '.m3u8' in lower:
            score += 200

        # AVOID LOW STREAMS
        if 'low' in lower:
            score -= 300

        # AVOID ADS
        if 'ad' in lower:
            score -= 1000

        if score > best_score:
            best_score = score
            best_stream = url

    return best_stream or streams[0].get('url', '')

# ============================================
# PROCESS CHANNELS
# ============================================

for channel_data in jsonresp['response']['data']:

    try:

        path = channel_data['target']['path']

        epg = channel_data['id']

        name = channel_data['display']['title']

        logo = (
            channel_data['display']['imageUrl']
            .replace(
                "common,",
                "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/"
            )
        )

        language = get_language(name)

        category = get_category(name)

        if language == "English":
            group_title = category
        else:
            group_title = f"{language} {category}"

        # ============================================
        # GET STREAM
        # ============================================

        encodedpath = urllib.parse.quote_plus(path)

        stream_url = (
            "https://yuppfast-api.revlet.net/service/api/v1/page/stream"
            f"?path={encodedpath}"
        )

        resp = http.request(
            "GET",
            stream_url,
            headers=channel_headers
        )

        stream = json.loads(
            resp.data.decode("utf-8")
        )

        final_stream = ""

        if stream.get('status') is True:

            streams = stream['response'].get(
                'streams',
                []
            )

            final_stream = get_best_stream(streams)

        # ============================================
        # PLAYLIST ENTRY
        # ============================================

        playlist.append(
            f'#EXTINF:-1 '
            f'tvg-id="{epg}" '
            f'tvg-chno="{epg}" '
            f'tvg-name="{name}" '
            f'tvg-logo="{logo}" '
            f'group-title="{group_title}",'
            f'{epg} {name}'
        )

        playlist.append(final_stream)

        print(f"Added: {name}")

    except Exception as e:

        print(f"Failed channel: {e}")

# ============================================
# WRITE PLAYLIST
# ============================================

with open(
    './yupptvfast.m3u',
    'w',
    encoding='utf-8'
) as f:

    for line in playlist:
        f.write(f"{line}\n")

print("Playlist updated successfully")

