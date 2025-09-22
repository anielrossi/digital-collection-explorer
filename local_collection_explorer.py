import os
import pandas as pd

import discogs_client

from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
from mutagen.id3 import ID3

#root_dir = "/Volumes/TOSHIBA/Rekordbox_database_selected"
#root_dir = "/Volumes/TOSHIBA/test_collection"
#root_dir = "/Users/aniel/digital-collection-explorer/test" 
root_dir = "/Volumes/CRUCIAL/Rekordbox Database"

data = []

for dirpath, dirnames, filenames in os.walk(root_dir):
     for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        # Check if the file is an MP3 file (you can adjust this check if needed)
        if file_path.lower().endswith(".mp3") and not file_path.split("/")[-1].lower().startswith("."):           
            try:
                id3file = ID3(file_path)
                comments = id3file.getall("COMM")
                extracted_texts = [comm.text[0] for comm in comments]
                mp3file = MP3(file_path, ID3=EasyID3)
                if(extracted_texts == []):
                    print('Empty comment section or Visit from bandcamp')
                    print(filename) 
                    data.append({
                        "Artist": mp3file.get("artist", [""])[0],
                        "Title": mp3file.get("title", [""])[0],
                        "Album": mp3file.get("album", [""])[0], 
                        "Path": file_path,
                        "OK/KO": "OK"
                    })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                data.append({
                    "Artist": "",
                    "Title": "",
                    "Album": "", 
                    "Path": file_path,
                    "OK/KO": "KO"
                })

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=["Artist", "Title", "Album", "Path", "OK/KO"])

print(len(df))

#Discogs client 
d = discogs_client.Client('tracklist_explorer', user_token='TQnLrfoPbUSIPjrwWqIkZSkuJczEwsHtQXbdegwL')

styles = []
genres = []
labels = []

print("start search")

for idx,i in df.iterrows():
    print(idx)
    try:
        #see if comment is populated (?) nah
        # put a flag for the ones already processed 
        #mp3file = MP3(file_path, ID3=EasyID3)
        #release = d.search(i["Artist"] + " " + i["Album"], type='release')[0]
        print(i["Artist"],i["Album"])
        release = d.search(i["Album"], artist=i["Artist"], type='release')[0]
        print(release)
        labels.append(release.labels[0].name)
        styles.append(release.styles)
        genres.append(release.genres)
    except:
        labels.append("error")
        styles.append("error")
        genres.append("error")

print("end search")

df["Style"] = styles
df["Genres"] = genres
df["Labels"] = labels

df.to_csv("df_local.csv")

#import pandas as pd

#df = pd.read_csv('df_clean_local.csv', index_col=0)
#df['Path'] = df.apply(lambda row: f"{root_dir}/{row['Artist']} - {row['Title']}.mp3", axis=1)

errors = df[(df["OK/KO"] == "KO") | (df["Genres"] == "error")]
df_final = df.drop(index=errors.index)

df_final.to_csv("df_clean_local.csv")
errors.to_csv('errors_local.csv')

"""
df_exploded = df_final.explode("style").drop("genres", axis=1)
set(df_exploded["style"])
df_exploded[df_exploded["style"] == "Ambient"]
df_exploded.to_csv("df_exploded_rekordbox.csv")
"""

print("---------writing labels---------")
for idx, i in df_final.iterrows():
    try:
        if (i["Labels"]) and i["Labels"] != "error":
            #for i in filez:
            mp3file = MP3(i["Path"], ID3=EasyID3)
            #organization corresponds to PUBLISHER
            mp3file["organization"] = i["Labels"]
            mp3file.save()
    except Exception as e:
        print("error:", e)

print("---------writing genres---------")
for idx, i in df_final.iterrows():
    try:
        genres_str = ""
        if (i["Style"]):
            #only if reading df
            #x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in i["Style"]:
                genres_str += genre + "|"
            #for i in filez:
            mp3file = MP3(i["Path"], ID3=EasyID3)
            mp3file["genre"] = i["Genres"][0]
            mp3file.save()
    except:
        print("error:", idx)

"""
print("---------delete comments---------")
for idx, i in df_final.iterrows():
    try:
        print(i)
        genres_str = ""
        if i["Style"]:
            #only if reading df
            #x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            #for i in filez:
            mp3file = ID3(i["Path"])
            mp3file.delall("COMM") 
            mp3file.save()
    except Exception as e:
        print("error:", e)
"""

print("---------writing comments---------")
for idx, i in df_final.iterrows():
    try:
        print(i)
        genres_str = ""
        if i["Style"]:
            #only if reading df
            #x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in i["Style"]:
                genres_str += genre + "|"
            mp3file = MP3(i["Path"], ID3=EasyID3)
            EasyID3.RegisterTextKey('comment', 'COMM')
            mp3file["comment"] = genres_str[:-1]
            mp3file.save()
    except Exception as e:
        print("error:", e)
