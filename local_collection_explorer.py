import os
import pandas as pd

import discogs_client

import glob
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
from mutagen.id3 import ID3, TCON, COMM

#Requirements:
# all files mp3 for tagging standard


root_dir = "/Volumes/TOSHIBA/Rekordbox_database_selected"

data = []

"""
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        # Check if the file is an MP3 file (you can adjust this check if needed)
        if file_path.lower().endswith(".mp3") and not file_path.split("/")[-1].lower().startswith("."):
            print(filename)            
            try:
                mp3file = MP3(file_path, ID3=EasyID3)
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
"""
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        
        # Check if the file is an MP3 file (you can adjust this check if needed)
        if file_path.lower().endswith(".mp3"):
            print(filename)
            print(file_path)
            
            try:
                mp3file = MP3(file_path, ID3=EasyID3)
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

#Discogs client 
d = discogs_client.Client('tracklist_explorer', user_token='TQnLrfoPbUSIPjrwWqIkZSkuJczEwsHtQXbdegwL')

styles = []
genres = []
labels = []

print("start search")

for idx,i in df.iterrows():
    print(idx)
    try:
        #release = d.search(i["Artist"] + " " + i["Album"], type='release')[0]
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

"""
import pandas as pd

df = pd.read_csv('df_clean_local.csv', index_col=0)

"""

errors = df[(df["OK/KO"] == "KO") | (df["Genres"] == "error")]
df_final = df.drop(index=errors.index)

df_final.to_csv("df_clean_local.csv")
errors.to_csv('errors_local.csv')


df_exploded = df_final.explode("style").drop("genres", axis=1)
set(df_exploded["style"])
df_exploded[df_exploded["style"] == "Ambient"]
df_exploded.to_csv("df_exploded_rekordbox.csv")


print("---------writing labels---------")
for idx, x in df_final.iterrows():
    try:
        filez = glob.glob(x["Path"])
        if (x["Labels"]) and x["Labels"] != "error":
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                mp3file["organization"] = x["Labels"]
                mp3file.save()
    except Exception as e:
        print("error:", e)

print("---------writing genres---------")
for idx, x in df_final.iterrows():
    try:
        filez = glob.glob(x["Path"])
        genres_str = ""
        if (x["Style"]):
            #only if reading df
            x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in x["Style"]:
                genres_str += genre + "|"
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                mp3file["genre"] = x["Style"][0]
                mp3file.save()
    except:
        print("error:", idx)

print("---------delete comments---------")
for idx, x in df_final.iterrows():
    try:
        print(x)
        filez = glob.glob(x["Path"])
        genres_str = ""
        if x["Style"]:
            #only if reading df
            #x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in x["Style"]:
                genres_str += genre + "|"
            for i in filez:
                mp3file = ID3(i)
                mp3file.delall("COMM") 
                mp3file.save()
    except Exception as e:
        print("error:", e)

print("---------writing comments---------")
for idx, x in df_final.iterrows():
    try:
        print(x)
        filez = glob.glob(x["Path"])
        genres_str = ""
        if x["Style"]:
            #only if reading df
            #x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in x["Style"]:
                genres_str += genre + "|"
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                EasyID3.RegisterTextKey('comment', 'COMM')
                mp3file["comment"] = genres_str[:-1]
                mp3file.save()
    except Exception as e:
        print("error:", e)