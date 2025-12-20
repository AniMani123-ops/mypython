from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

def get_youtube_service(api_key):
    """Initializes the YouTube Data API service."""
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        return None

def search_channels(service, query, max_results=10):
    """Searches for channels based on a query."""
    if not service or not query:
        return []
    
    try:
        request = service.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=max_results
        )
        response = request.execute()
        
        channels = []
        for item in response.get("items", []):
            channels.append({
                "id": item["snippet"]["channelId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            })
        return channels, None
    except HttpError as e:
        error_message = f"An HTTP error {e.resp.status} occurred: {e.content}"
        print(error_message)
        return None, error_message

def get_channel_stats(service, channel_ids):
    """Retrieves statistics for a list of channel IDs."""
    if not service or not channel_ids:
        return pd.DataFrame()

    try:
        request = service.channels().list(
            part="snippet,statistics",
            id=",".join(channel_ids)
        )
        response = request.execute()

        stats_list = []
        for item in response.get("items", []):
            stats = item["statistics"]
            snippet = item["snippet"]
            stats_list.append({
                "Channel Name": snippet["title"],
                "Subscribers": int(stats.get("subscriberCount", 0)),
                "Total Views": int(stats.get("viewCount", 0)),
                "Video Count": int(stats.get("videoCount", 0)),
                "Thumbnail": snippet["thumbnails"]["default"]["url"]
            })
        
        return pd.DataFrame(stats_list)
    except HttpError as e:
        print(f"An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        return pd.DataFrame()

def get_latest_live_stream_stats(service, channel_id):
    """Retrieves stats for the most recent live stream of a channel."""
    if not service or not channel_id:
        return None

    try:
        # 1. Search for completed broadcasts (most recent first)
        request = service.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="completed",
            type="video",
            order="date",
            maxResults=1
        )
        response = request.execute()
        
        # If no completed, try 'live'
        if not response.get("items"):
             request = service.search().list(
                part="snippet",
                channelId=channel_id,
                eventType="live",
                type="video",
                order="date",
                maxResults=1
            )
             response = request.execute()

        if not response.get("items"):
            return None

        video_id = response["items"][0]["id"]["videoId"]
        snippet = response["items"][0]["snippet"]

        # 2. Get Video Statistics
        stats_request = service.videos().list(
            part="statistics, liveStreamingDetails",
            id=video_id
        )
        stats_response = stats_request.execute()
        
        if not stats_response.get("items"):
             return None
             
        stats = stats_response["items"][0]["statistics"]
        
        return {
            "title": snippet["title"],
            "published_at": snippet["publishedAt"], # Original start time
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "video_id": video_id
        }

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

POPULAR_NEWS_CHANNELS = {
    "BBC News": "UC16niRr50-MSBwiO3YDb3RA",
    "CNN": "UCupvZG-5ko_eiXAupbDfxWw",
    "Al Jazeera English": "UCUXOv7jJktj19aeA6TAq2wA",
    "NDTV": "UCZFMm1Hin_qO758Wl_FRf6A",
    "Aaj Tak": "UCt4t-jeY85JegMlZ-E5UWtA",
    "Fox News": "UCXIJgqnII2ZOINSWNOGFThg",
    "MSNBC": "UCkR-Rgce_5WkHTlpGphrQjA",
    "Sky News": "UCoMdktPbSTixAyNGwb-UYkQ",
    "NBC News": "UCeY0bbntWzzVIaj2z3QigXg",
    "ABC News": "UCBi2mrWuNuyYy4gbM6fU18Q"
}
