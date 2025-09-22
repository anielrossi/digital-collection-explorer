import os
import pandas as pd
import discogs_client
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

#root_dir = "/Volumes/CRUCIAL/Rekordbox Database"
root_dir = "test"
output_csv = "df_local.csv"

# Initialize discogs client
d = discogs_client.Client('tracklist_explorer', user_token='TQnLrfoPbUSIPjrwWqIkZSkuJczEwsHtQXbdegwL')

# Load already processed paths if CSV exists
if os.path.exists(output_csv):
    df_existing = pd.read_csv(output_csv)
    processed_paths = set(df_existing["Path"].tolist())
else:
    df_existing = pd.DataFrame()
    processed_paths = set()

def process_file(file_path):
    try:
        id3file = ID3(file_path)
        comments = id3file.getall("COMM")
        extracted_texts = [comm.text[0] for comm in comments]
        mp3file = MP3(file_path, ID3=EasyID3)

        if extracted_texts != []:
            return None  # skip files that already have comments

        artist = mp3file.get("artist", [""])[0]
        title = mp3file.get("title", [""])[0]
        album = mp3file.get("album", [""])[0]

        # Query Discogs
        try:
            release = d.search(album, artist=artist, type="release")[0]
            label = release.labels[0].name
            style = release.styles
            genre = release.genres
            ok = "OK"
        except Exception:
            label, style, genre, ok = "error", "error", "error", "KO"

        # Write tags back into the file
        if label != "error":
            mp3file["organization"] = label
        if genre != "error":
            mp3file["genre"] = genre[0]
        if style != "error":
            EasyID3.RegisterTextKey("comment", "COMM")
            mp3file["comment"] = "|".join(style)
        mp3file.save()

        return {
            "Artist": artist,
            "Title": title,
            "Album": album,
            "Path": file_path,
            "OK/KO": ok,
            "Labels": label,
            "Style": style,
            "Genres": genre,
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            "Artist": "",
            "Title": "",
            "Album": "",
            "Path": file_path,
            "OK/KO": "KO",
            "Labels": "error",
            "Style": "error",
            "Genres": "error",
        }

# Walk the filesystem and process each file
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        if (
            file_path.lower().endswith(".mp3")
            and not filename.lower().startswith(".")
            and file_path not in processed_paths
        ):
            print(f"Processing: {filename}")
            result = process_file(file_path)
            if result:
                # Append result to CSV immediately
                df_row = pd.DataFrame([result])
                df_row.to_csv(output_csv, mode="a", header=not os.path.exists(output_csv), index=False)
