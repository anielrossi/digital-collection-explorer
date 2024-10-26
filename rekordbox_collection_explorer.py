import os
import pandas as pd

import discogs_client

import glob
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
from mutagen.id3 import ID3, TCOM, COMM


root_dir = "/Volumes/SANDISK1/Contents"
data = []

# Iterate over one level of subdirectories and list their contents
for subdir in os.listdir(root_dir):
    subdir_path = os.path.join(root_dir, subdir)
    if os.path.isdir(subdir_path):
        # Print each item in the subdirectory with the format "subdir - item"
        for item in os.listdir(subdir_path):
            data.append({"Artist": subdir, "Album": item, "Path": subdir_path + "/" + item})

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=["Artist", "Album", "Path"])

#Discogs client 
d = discogs_client.Client('tracklist_explorer', user_token='TQnLrfoPbUSIPjrwWqIkZSkuJczEwsHtQXbdegwL')

styles = []
genres = []
labels = []

for idx,i in df.iterrows():
    try:
        release = d.search(i["Artist"] + " " + i["Album"], type='release')[0]
        labels.append(release.labels[0].name)
        styles.append(release.styles)
        genres.append(release.genres)
    except:
        labels.append("error")
        styles.append("error")
        genres.append("error")

df["Style"] = styles
df["Genres"] = genres
df["Labels"] = labels

df.to_csv("df_rekordbox.csv")

# %%
df["style"].value_counts()

# %%
errors = df[df["labels"] == "error"]
df_final = df.drop(index=errors.index)
merged_df = df_final.merge(df)

merged_df.to_csv("df_clean_rekordbox.csv")
errors.to_csv('errors_rekordbox.csv')

"""
df_exploded = df_final.explode("style").drop("genres", axis=1)
set(df_exploded["style"])
df_exploded[df_exploded["style"] == "Ambient"]
df_exploded.to_csv("df_exploded_rekordbox.csv")
"""

for idx, x in merged_df.iterrows():
    print(idx, x["Path"])
    try:
        filez = glob.glob(os.path.join(x["Path"], '*.mp3'))
        if (x["labels"]):
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                mp3file["organization"] = x["labels"]
                mp3file.save()
    except Exception as e:
        print("error:", e)

for idx, x in merged_df.iterrows():
    try:
        filez = glob.glob(os.path.join(x["Path"], '*.mp3'))
        genres_str = ""
        if (x["Style"]):
            for genre in x["Style"]:
                genres_str += genre + "|"
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                mp3file["genre"] = x["Style"][0]
                mp3file.save()
    except:
        print("error:", idx)

for idx, x in merged_df.iterrows():
    try:
        filez = glob.glob(os.path.join(x["Path"], '*.mp3'))
        genres_str = ""
        if x["style"]:
            for genre in x["style"]:
                genres_str += genre + "|"
            print(genres_str)
            for i in filez:
                mp3file = ID3(i)
                #from old script
                #mp3file["TCON"] = TCON(encoding=3, text=genre)
                mp3file["COMM"] = COMM(encoding=3, text=genres_str[:-1])
                #mp3file.add(COMM(encoding=3, text=genres_str[:-1]))
                mp3file.save()
    except:
        print("error:", idx)
