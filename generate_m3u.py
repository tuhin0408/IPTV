import os
import json
import requests

def fetch_and_filter():
    # Load servers array from GitHub Secret environment variable
    servers_json = os.environ.get("XTREAM_SERVERS")
    if not servers_json:
        print("Error: XTREAM_SERVERS secret is empty or missing.")
        return

    servers = json.loads(servers_json)
    m3u_lines = ["#EXTM3U\n"]
    
    # Target keywords for matching channels
    keywords = ["fifa", "worldcup", "world cup"]

    for idx, srv in enumerate(servers, start=1):
        base_url = srv["url"].rstrip("/")
        user = srv["username"]
        passwd = srv["password"]
        
        # Xtream Codes Player API Endpoint
        api_url = f"{base_url}/player_api.php?username={user}&password={passwd}&action=get_live_streams"
        print(f"Connecting to Server {idx}...")
        
        try:
            response = requests.get(api_url, timeout=20)
            if response.status_code != 200:
                print(f"Skipping Server {idx}: Received status code {response.status_code}")
                continue
                
            streams = response.json()
            if not isinstance(streams, list):
                print(f"Skipping Server {idx}: Unexpected response format.")
                continue

            count = 0
            for item in streams:
                name = item.get("name", "")
                # Case-insensitive phrase check
                if any(kw in name.lower() for kw in keywords):
                    stream_id = item.get("stream_id")
                    container = item.get("container_extension", "ts")
                    group = item.get("category_name", f"Server {idx}-FIFA")
                    logo = item.get("stream_icon", "")

                    # Construct structural Xtream streaming link format
                    # Format: http://domain:port/username/password/stream_id.ts
                    stream_url = f"{base_url}/{user}/{passwd}/{stream_id}.{container}"
                    
                    # Generate standard M3U track entry
                    m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n')
                    m3u_lines.append(f"{stream_url}\n")
                    count += 1
            
            print(f"Found {count} matching FIFA channels on Server {idx}.")
            
        except Exception as e:
            print(f"Failed to fetch data from Server {idx}: {str(e)}")

    # Write out to local repository context file
    with open("fifa_worldcup.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)
    print("Playlist generation complete!")

if __name__ == "__main__":
    fetch_and_filter()
