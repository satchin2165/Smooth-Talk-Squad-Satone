import streamlit as st
import requests
import wave
from tensorflow import keras
import numpy as np
import os
from tqdm import tqdm
from audio.splitter import splitter
from params import *
from prediction.preprocessor import preprocess_features
from prediction.registry import load_model

VOICE_SPLITS_DIRECTORY = os.path.join("audio","splits")


def goToChallenge(challenge_name):
    st.session_state.place = (
        challenge_name  # we are moving our character to other scene (e.g. sheepScene)
    )
    st.experimental_rerun()  # rerun is streamlit specific and rerund the app

def getPredictResult():
    if PREDICT_RESOURCE == 'remote':
        # Send the voice data to backend
        url = 'http://localhost:8000/predict/'
        files = {'file': open('output.wav', 'rb')}
        response = requests.post(url, files=files)
        return np.array(response.json()) # expect to be an array of y value

    elif PREDICT_RESOURCE == 'local':
        # Split the audio into clips
        splitter('output.wav')
        # Use model to predict
        model = load_model()
        assert model is not None
        model.summary() # Keep for debugging purpose
        X_processed = preprocess_features()
        y_pred = model.predict(X_processed)
        print(f"predict:{y_pred}") # Keep for debugging purpose
        delete_files_in_directory(VOICE_SPLITS_DIRECTORY)
        return y_pred



def createAudioFile(wav_byte_data):
    file_name = "output.wav"
    sample_rate = 44100
    with wave.open(file_name, "wb") as wf:
        wf.setnchannels(2)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(wav_byte_data)

def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print(f"All files in {directory_path} deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")