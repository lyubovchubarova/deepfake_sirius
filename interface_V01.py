#Testing text2speech model

from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
from voice_generator import VoiceGenerator
import torch
import soundfile as sf
#from playsound import playsound
import pygame
import sys
import random
import threading
import winsound
import time
import os
#import mutagen
from mutagen.wave import WAVE 



S:str = "ABEGIMOUZ" #the most important sounds
nxt_video = 0
AUD_done:bool = True
VID_done:bool = True

voice_generator = VoiceGenerator()

#dict (letter : image of this sound)
d = dict()
for i in S:
    d[i] = pygame.image.load("animation\\" + i + ".png")
d[' '] = pygame.image.load("animation\\" + 'M' + ".png")

#returns color Red, Green or Blue(randomly)
def rand_col() -> tuple:
    x: int = random.randint(0, 2)
    if x == 0:
        return (255, 0, 0)
    if x == 1:
        return (0, 255, 0)
    return (0, 0, 255)

#plays created sound


def play_sd(num_sound: int) -> None:
    global AUD_done
    AUD_done = False
    pth = f"C:\\Users\\Home\\.spyder-py3\\speech{num_sound}.wav"
    winsound.PlaySound(pth, winsound.SND_FILENAME)
    AUD_done = True
    

#makes letters bigger
def to_up(s: str) -> str:
    if 'a' <= s <= 'z':
        return chr(ord(s) - ord('a') + ord('A'))
    return s

#shows sprites with right durations

pygame.init()
 #window parameters
n: int = 250
m: int = 200
FPS: int = 30
screen = pygame.display.set_mode((n, m))

def create_wav(TEXT: str, num_aud: int) -> None:
    vg.generate(TEXT, os.getcwd(), f"speech{num_aud}.wav")


def show_pics(text: str, ln: int, num_video: int) -> None:
    global VID_done
    VID_done = False

    global FPS, screen
    
    #if nxt_video == False:
        
    #nxt_video = False

    clock = pygame.time.Clock()
    
    #how much iteratoins of showing cycle are required to show one sprite
    sprite_iterations:float = ln / len(text) * FPS / 1000

    print(sprite_iterations)
    i = 0
    animation_set = [''] * len(text)
    
    for e in text:
        u = to_up(e)
        if u in S:
            animation_set[i] = d[u]
        else:
            animation_set[i] = d[' ']
        i += 1
        
    print("Done1")
    i = 0
    iters = 0

    #cycle to show the video
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if(iters >= sprite_iterations*i):
            #if i < len(animation_set):
            screen.fill((0, 0, 0))
            screen.blit(animation_set[i%len(animation_set)], (10, 10))
            i += 1

        iters += 1
        if i >= len(animation_set):
            #pygame.quit()
            #sys.exit()
            #nxt_video = True
            VID_done = True
            return
        pygame.display.flip()
        clock.tick(FPS)


TEXT = 'Hello, I do not know how to make videos. Please help me! This is very difficult.'



#decomment next strings to include text2speech model(it will create .wav file of TEXT)

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

texts = []
current = ''
for i in TEXT:
    if i in {'.',',','!','?'} and current != '':
        texts.append(current)
        current = ''
    else:
        if(current != '' or i != ' '):
            current += i

for i in range(len(texts)):
    create_wav(texts[i], i)

for i in range(len(texts)):
    snd = WAVE(f"speech{i}.wav")
    duration = snd.info.length * 1000
    t1 = threading.Thread(target=play_sd, args=(i,), daemon=True)
    t2 = threading.Thread(target=show_pics, args=(texts[i],duration,i,), daemon=True)
    t2.start()
    t1.start()
    t2.join()
    t1.join()
    while((VID_done and AUD_done) == False):
        time.sleep(0.1)



#play_sd()
#show_pics(TEXT, duration)

#using THREADS to show video and play sound in one time


pygame.quit()
sys.exit()

