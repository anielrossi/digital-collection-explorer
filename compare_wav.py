import wave
import numpy as np

def compare_wav_files(file1_path, file2_path):
    # Open the first file
    with wave.open(file1_path, 'rb') as file1:
        params1 = file1.getparams()  # Metadata of file 1
        frames1 = file1.readframes(params1.nframes)  # Raw frame data of file 1
    
    # Open the second file
    with wave.open(file2_path, 'rb') as file2:
        params2 = file2.getparams()  # Metadata of file 2
        frames2 = file2.readframes(params2.nframes)  # Raw frame data of file 2

    # Step 1: Compare metadata
    if params1 != params2:
        print("Files are not identical (different metadata).")
        return False

    # Step 2: Convert frames to numpy arrays for comparison
    audio_data1 = np.frombuffer(frames1, dtype=np.int16)
    audio_data2 = np.frombuffer(frames2, dtype=np.int16)

    # Step 3: Compare audio data
    if np.array_equal(audio_data1, audio_data2):
        print("Files are identical.")
        return True
    else:
        print("Files are not identical (different audio data).")
        return False

# Example usage
file1_path = '/Users/aniel/Desktop/analogcut_a-sindrome-not-now-master-digital-wav_2024-10-24_1624/AA.Sindrome - Not Today [Master Vinyl].wav'
file2_path = '/Users/aniel/Desktop/analogcut_a-sindrome-not-now-master-digital-v2-wav_2024-11-01_1756/AA.Sindrome - Not Today [Master Vinyl] V2.wav'
file3_path = '/Users/aniel/Desktop/analogcut_a-sindrome-not-now-master-vinyl-v3-wav_2024-11-08_1432/AA.Sindrome - Not Today [Master Vinyl] V3.wav'
compare_wav_files(file1_path, file2_path)
compare_wav_files(file2_path, file3_path)
compare_wav_files(file1_path, file3_path)
