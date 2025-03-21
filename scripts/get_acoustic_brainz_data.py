# import zstandard
# import tarfile
# import os
from pathlib import Path
import pprint
import json
import certifi
import requests
import musicbrainzngs
from typing import Optional

# refer to /notes/de_spotify.txt


def ingest_json(input_dir: str):
    input_dir = Path(input_dir)
    tracks = []
    for file in input_dir.iterdir():
        with open(file, 'r') as f:
            data = json.load(f)
            # pprint.pprint(data)
            track = {
                'musicbrainz_recordingid': data['metadata']['tags']['musicbrainz_recordingid'][0],
                'title': data['metadata']['tags'].get('title', [""])[0],
                'artist': data['metadata']['tags'].get('artist', [""])[0],
                'album': data['metadata']['tags'].get('album', [""])[0],
                # 'bpm': int(data['metadata']['tags'].get('bpm', [])[0]),
                'danceable': float(data['highlevel']['danceability']['all']['danceable']),
                'aggressive': float(data['highlevel']['mood_aggressive']['all']['aggressive']),
                'electronic': float(data['highlevel']['mood_electronic']['all']['electronic']),
                'acoustic': float(data['highlevel']['mood_acoustic']['all']['acoustic']),
                'happy': float(data['highlevel']['mood_happy']['all']['happy']),
                'party': float(data['highlevel']['mood_party']['all']['party']),
                'relaxed': float(data['highlevel']['mood_relaxed']['all']['relaxed']),
                'sad': float(data['highlevel']['mood_sad']['all']['sad']),
                'dark': float(data['highlevel']['timbre']['all']['dark']),
                'tonal': float(data['highlevel']['tonal_atonal']['all']['tonal']),
                'voice': float(data['highlevel']['voice_instrumental']['all']['voice'])
            }
            tracks.append(track)
    return tracks


def decompress_and_extract(input_file_path, output_dir=None):
    """
    Decompress a .tar.zst file and extract its contents
    
    Args:
        input_file_path (str): Path to the .tar.zst file
        output_dir (str, optional): Directory to extract contents to. Defaults to current directory.
    """
    input_path = Path(input_file_path)
    
    if not input_path.exists():
        print(f"Error: File {input_file_path} not found")
        return
        
    # Create temporary .tar file name
    tar_path = input_path.with_suffix('')  # Remove .zst extension
    
    try:
        # Step 1: Decompress .zst to .tar
        print(f"Decompressing {input_path.name}...")
        with open(input_path, 'rb') as input_file:
            dctx = zstandard.ZstdDecompressor()
            with open(tar_path, 'wb') as output_file:
                dctx.copy_stream(input_file, output_file)
        
        # Step 2: Extract .tar file
        print(f"Extracting {tar_path.name}...")
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(path=output_dir)
            
        print("Extraction complete!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        # Clean up: remove temporary .tar file
        if tar_path.exists():
            os.remove(tar_path)
            print(f"Cleaned up temporary file: {tar_path.name}")

def setup_musicbrainz():
    musicbrainzngs.set_useragent(
        "wave_guide",
        "0.1"
    )
     # Use certifi's certificate bundle
    musicbrainzngs.set_hostname("musicbrainz.org", False)

def get_streaming_service_url(mbid: str) -> Optional[dict]:
    """
    Get official streaming URLs for a MusicBrainz recording ID using ListenBrainz API
    """
    # ListenBrainz API endpoint
    url = f"https://api.listenbrainz.org/1/metadata/recording/{mbid}/links"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'links' in data:
            return {
                'spotify_url': next((link['url'] for link in data['links'] 
                                  if link['catalog'] == 'spotify'), None),
                'apple_music_url': next((link['url'] for link in data['links'] 
                                       if link['catalog'] == 'apple_music'), None),
                'youtube_music_url': next((link['url'] for link in data['links'] 
                                         if link['catalog'] == 'youtube_music'), None),
                'bandcamp_url': next((link['url'] for link in data['links'] 
                                    if link['catalog'] == 'bandcamp'), None),
            }
    except Exception as e:
        print(f"Error fetching streaming links: {e}")
    return None

def get_track_info(mbid: str) -> Optional[dict]:
    """
    Get recording information from MusicBrainz
    """
    try:
        result = musicbrainzngs.get_recording_by_id(
            mbid, 
            includes=["artist-credits", "releases"]
        )
        recording = result["recording"]
        
        return {
            'title': recording["title"],
            'artist': recording["artist-credit"][0]["artist"]["name"],
            'streaming_urls': get_streaming_service_url(mbid)
        }
    except Exception as e:
        print(f"Error fetching MusicBrainz data: {e}")
    return None

if __name__ == "__main__":
    # Set up MusicBrainz first
    setup_musicbrainz()
    
    # Example usage
    mbid = "b1a9c0e9-d987-4042-ae91-78d6a3267d69" # bohemian rhapsody
    track_info = get_track_info(mbid)
    
    if track_info:
        pprint.pprint(track_info)
        # print(f"Track: {track_info['title']}")
        # print(f"Artist: {track_info['artist']}")
        if track_info['streaming_urls']:
            print("\nStreaming URLs:")
            for service, url in track_info['streaming_urls'].items():
                if url:
                    print(f"{service}: {url}")
