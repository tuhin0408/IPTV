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
    """Scans the source playlist and extracts ONLY the m3u8 link."""
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF") and channel_name in line.upper():
            for j in range(i + 1, len(lines)):
                current_line = lines[j].strip()
                if current_line.startswith("#EXTINF"):
                    break
                if current_line.startswith("http") and "m3u8" in current_line:
                    return current_line
    return None

def update_local_file(file_path, new_url):
    """Updates only the stream link in the local file, preserving all other tags."""
    # If the file doesn't exist yet, create it with a basic structure
    if not os.path.exists(file_path):
        ensure_dir(file_path)
        with open(file_path, "w") as f:
            f.write(f"#EXTM3U\n{new_url}\n")
        return

    # Read the existing file to preserve tags like #EXTVLCOPT
    with open(file_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    link_replaced = False

    for line in lines:
        # The actual stream link is the only line that starts directly with "http".
        # Tags like user-agents start with "#" (e.g., #EXTVLCOPT:http-user-agent=...)
        if line.strip().startswith("http") and not link_replaced:
            # Swap in the new URL
            updated_lines.append(f"{new_url}\n")
            link_replaced = True
        else:
            # Keep the existing line (like your custom user agent)
            updated_lines.append(line)

    # If there was no http link to replace (e.g., broken file), append it
    if not link_replaced:
        updated_lines.append(f"{new_url}\n")

    # Write the preserved content + the new link back to the file
    with open(file_path, "w") as f:
        f.writelines(updated_lines)

def main():
    # Fetch the latest source playlist
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

    # Update TF-1
    if url_1:
        update_local_file(TARGET_1, url_1)
        print(f"Updated TF-1 with new link: {url_1}")
    else:
        print("Could not find m3u8 link for FIFA WC CHANNEL 1.")

    # Update TF-6
    if url_6:
        update_local_file(TARGET_6, url_6)
        print(f"Updated TF-6 with new link: {url_6}")
    else:
        print("Could not find m3u8 link for FIFA WC CHANNEL 6.")

if __name__ == "__main__":
    main()
