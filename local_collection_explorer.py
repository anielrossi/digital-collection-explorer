import os
import pandas as pd

import discogs_client

import glob
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
from mutagen.id3 import ID3, TBPM

import numpy as np
from pydub import AudioSegment
import librosa

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
#df['Path'] = df.apply(lambda row: f"{root_dir}/{row['Artist']} - {row['Title']}.mp3", axis=1)

errors = df[(df["OK/KO"] == "KO") | (df["Genres"] == "error")]
df_final = df.drop(index=errors.index)

#df_final.to_csv("df_clean_local.csv")
#errors.to_csv('errors_local.csv')

"""
df_exploded = df_final.explode("style").drop("genres", axis=1)
set(df_exploded["style"])
df_exploded[df_exploded["style"] == "Ambient"]
df_exploded.to_csv("df_exploded_rekordbox.csv")
"""

"""
print("---------writing labels---------")
for idx, x in df_final.iterrows():
    try:
        filez = glob.glob(x["Path"])
        if (x["Labels"]) and x["Labels"] != "error":
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                #organization corresponds to PUBLISHER
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
            x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in x["Style"]:
                genres_str += genre + ", "
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                EasyID3.RegisterTextKey('comment', 'COMM')
                mp3file["comment"] = genres_str[:-2]
                mp3file.save()
    except Exception as e:
        print("error:", e)


print("---------writing styles---------")
for idx, x in df_final.iterrows():
    try:
        print(x)
        filez = glob.glob(x["Path"])
        genres_str = ""
        if x["Style"]:
            #only if reading df
            x["Style"] = x["Style"].strip('][').replace("'", "").split(', ')
            ###
            for genre in x["Style"]:
                genres_str += genre + ", "
            for i in filez:
                mp3file = MP3(i, ID3=EasyID3)
                mp3file["style"] = genres_str[:-2]
                mp3file.save()
    except Exception as e:
        print("error:", e)
"""

def load_mp3_with_pydub(file_path):
    try:
        # Load the MP3 file with pydub
        print(f"Loading MP3 file: {file_path}")
        audio = AudioSegment.from_mp3(file_path)
        
        # Convert audio data to a NumPy array
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        
        # Convert to mono if stereo
        if audio.channels == 2:
            print("Converting stereo to mono")
            samples = samples.reshape((-1, 2)).mean(axis=1)
        
        # Normalize samples to range between -1 and 1 (librosa compatibility)
        samples /= np.iinfo(audio.array_type).max
        print(f"Loaded {len(samples)} samples with frame rate {audio.frame_rate}")
        
        # Return samples and sample rate
        return samples, audio.frame_rate
    except Exception as e:
        print(f"Error loading MP3 file: {e}")
        return None, None

def analyze_bpm(file_path):
    # Load audio data with pydub
    y, sr = load_mp3_with_pydub(file_path)
    
    if y is None or sr is None:
        print("Failed to load audio data.")
        return None
    
    # Calculate the onset envelope and tempo
    try:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Ensure that tempo is a number before returning
        if np.isnan(tempo):
            print("Tempo calculation failed or returned an invalid value.")
            return None
        
        print(f"Estimated BPM: ", int(round(tempo[0])))
        return int(round(tempo[0]))
    
    except Exception as e:
        print(f"Error calculating BPM: {e}")
        return None

def write_bpm_to_mp3(file_path, bpm):
    try:
        # Load the MP3 file with mutagen
        audio = MP3(file_path, ID3=ID3)
        
        # Add an ID3 tag if none exists
        if audio.tags is None:
            audio.add_tags()
        
        # Add or update the BPM tag
        audio.tags.add(TBPM(encoding=3, text=str(bpm)))
        audio.save()
        
        print(f"BPM written to {file_path}: {bpm} BPM")
    except Exception as e:
        print(f"Error writing BPM to MP3: {e}")

for idx, x in df_final.iloc[:1].iterrows():
    try:
        print(x["Path"])
        audio_file_path = x["Path"]
        bpm = analyze_bpm(audio_file_path)
        print(bpm)
        if bpm is not None:
            write_bpm_to_mp3(audio_file_path, bpm)
    except Exception as e:
        print("error:", e)