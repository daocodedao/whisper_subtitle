import numpy as np
import librosa
import soundfile as sf
from scipy.io import wavfile



# import sounddevice as sf
# https://github.com/CodeWiza/Voice-Conversion/blob/main/MiniProj23.py

def modify_speed(audio, speed_factor):
    y_speed = librosa.effects.time_stretch(audio, rate=1/speed_factor)
    modified_audio = np.column_stack((y_speed,))
    return modified_audio

def modify_speed_and_timbre(audio, speed_factor, timbre_factor):
    # Time stretching
    y_speed = librosa.effects.time_stretch(audio, rate=1/speed_factor)
    # Timbre modification (preemphasis)
    y_timbre = librosa.effects.preemphasis(y_speed, coef=timbre_factor)
    modified_audio = np.column_stack((y_timbre,))
    return modified_audio

videoPath="./sample/simple5.mp4"
videoMutePath="./sample/simple5_mute.mp4"
videoCnPath="./sample/simple5-cn.mp4"

outSrtEnPath="./sample/simple5-en.srt"
outSrtCnPath="./sample/simple5-cn.srt"
language="en"

combine_mp3_path = "./sample/simple5-combine.mp3"
combine_mp3_speed_path = "./sample/simple5-combine-speed.mp3"

song, fs = librosa.load(combine_mp3_path)
song_2_times_faster = librosa.effects.time_stretch(song, rate=1.2)
wavfile.write(combine_mp3_speed_path, fs, song_2_times_faster) # save the song
# librosa.output.write_wav(combine_mp3_speed_path, song_2_times_faster, fs)
# pitch_factor = 0.85 # Example: Changing the pitch to make it lower
# speed_factor = 0.8  # Adjust as needed
# timbre_factor = 100


# y_modified = np.interp(np.arange(0, len(song), pitch_factor), np.arange(len(song)), song).astype('float32')
# enhanced_audio = modify_speed_and_timbre(y_modified.flatten(), speed_factor, timbre_factor)



# sf.write(output_file_path, y_foreground, samplerate=44100, subtype='PCM_24')
# wavfile.write(combine_mp3_speed_path, fs, enhanced_audio) # save the song
