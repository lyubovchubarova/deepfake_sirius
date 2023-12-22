import os  # работа с файловой системой
import yaml

import pygame
import cv2
import winsound
import threading
import time
import sys
import replicate
GEN = False



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

GEN = True
def play_sd(path: str) -> None:
    global AUD_done
    AUD_done = False
    winsound.PlaySound(path, winsound.SND_FILENAME)
    AUD_done = True

def show_video(path: str) -> None:
    global VID_done
    VID_done = False
    captured = cv2.VideoCapture(path)
    is_ok, vid = captured.read()
    global clock, FPS
    
    while(is_ok):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                #is_ok = False
        is_ok, vid = captured.read()
        if is_ok:
            to_show = pygame.image.frombuffer(vid.tobytes(), vid.shape[1::-1], "BGR")
        screen.blit(to_show, (0, 0))
        pygame.display.flip()
        
        if is_ok == False:
            VID_done = True
            return
            captured = cv2.VideoCapture(PATH_VID)
            is_ok, vid = captured.read()
            
def show_static_picture(path: str) -> None:
    global VID_done, clock, FPS, GEN
    if VID_done and GEN:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return
        to_show = pygame.image.load(path)
        screen.blit(to_show, (0, 0))
        pygame.display.flip()
        
            
def play_video_with_sound(path: str, wav_path: str) -> None:
    t1 = threading.Thread(target=play_sd, args=(wav_path,), daemon=True)
    t2 = threading.Thread(target=show_video, args=(path,), daemon=True)
    t2.start()
    t1.start()
    t2.join()
    t1.join()
    while(AUD_done == False or VID_done == False):
        time.sleep(0.01)
        
def ask() -> str:
    output = replicate.run(
        var["interface_serv"],
        input={"face": open(path_to_static, "rb"),
              "audio": open(PATH_AUD, "rb")}
    )
    return output