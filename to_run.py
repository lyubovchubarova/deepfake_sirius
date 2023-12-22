import os  # работа с файловой системой
import yaml
import urllib.request
import time
from mutagen.wave import WAVE 


import voice_recognition
import answer_creator
import interface
#ST


import pygame



with open('config.yaml') as f:
    var = yaml.load(f, Loader=yaml.FullLoader)

with open('keys.yaml') as f:
    key = yaml.load(f, Loader=yaml.FullLoader)
    
os.environ["REPLICATE_API_TOKEN"] = key["interface"]

PATH_TO_MODEL = os.getcwd() + var["PATH_TO_MODEL"]
PATH_TO_OUTPUT = os.getcwd() + var["PATH_TO_OUTPUT"]

pygame.init()
clock = pygame.time.Clock()

PATH_VID = os.getcwd() + var["PATH_VID"]
PATH_AUD = os.getcwd() + var["PATH_AUD"]
path_to_static = os.getcwd() + var["path_to_static"]

n = var["width"]
m = var["height"]
FPS = var["FPS"]
screen = pygame.display.set_mode((n, m))
AUD_done = True
VID_done = True


if __name__ == "__main__":
    querries = []
    iq = 0
    
    while True:
        if(len(querries) == iq):
            interface.show_static_picture(path_to_static)
            time.sleep(0.02)
        else:
            a = querries[iq][0]
            b = querries[iq][1]
            interface.play_video_with_sound(a, b)
            iq += 1
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = voice_recognition.record_and_recognize_audio()
        os.remove("microphone-results.wav")
        
        path_to_file = answer_creator.ask(voice_input)
        snd = WAVE(path_to_file)
            
        output = interface.ask()

        urllib.request.urlretrieve(output, PATH_VID)
        querries.append([PATH_VID, PATH_AUD])

        




