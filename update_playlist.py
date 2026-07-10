import os
import urllib.request

# The source auto-updating playlist
SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/Toffee-Auto-Update-Playlist/refs/heads/main/toffee_playlist.m3u"

# Target files in your repository
TARGET_1 = "playlist/TF/TF-1.m3u8"
TARGET_6 = "playlist/TF/TF-6.m3u8"

def ensure_dir(file_path):
    """Ensure the directory exists before writing."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def extract_m3u8_link(lines, channel_name):
    """Scans the playlist lines for a specific channel and extracts ONLY its m3u8 link."""
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF") and channel_name in line.upper():
            # Scan forward from the channel name
            for j in range(i + 1, len(lines)):
                current_line = lines[j].strip()
                
                # If we hit the next channel before finding a link, stop looking
                if current_line.startswith("#EXTINF"):
                    break
                    
                # Strictly capture only the line that is an HTTP link ending in/containing m3u8
                if current_line.startswith("http") and "m3u8" in current_line:
                    return current_line
    return None

def main():
    # Fetch the latest playlist
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            lines = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error fetching source playlist: {e}")
        return

    # Scrape the specific links
    url_1 = extract_m3u8_link(lines, "FIFA WC CHANNEL 1")
    url_6 = extract_m3u8_link(lines, "FIFA WC CHANNEL 6")

    # Save to TF-1
    if url_1:
        ensure_dir(TARGET_1)
        with open(TARGET_1, "w") as f:
            # Writing the standard m3u header + the raw m3u8 link
            f.write(f"#EXTM3U\n{url_1}\n")
        print(f"Scraped TF-1: {url_1}")
    else:
        print("Could not find m3u8 link for FIFA WC CHANNEL 1.")

    # Save to TF-6
    if url_6:
        ensure_dir(TARGET_6)
        with open(TARGET_6, "w") as f:
            f.write(f"#EXTM3U\n{url_6}\n")
        print(f"Scraped TF-6: {url_6}")
    else:
        print("Could not find m3u8 link for FIFA WC CHANNEL 6.")

if __name__ == "__main__":
    main()
