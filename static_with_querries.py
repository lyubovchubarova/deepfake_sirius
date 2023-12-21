#из-за потоков нельзя закрыть окно во время того, как Павел Воля говорит

import pygame
import cv2
import winsound
import threading
import time
import sys
#"C:\Users\Home\Downloads\nw.mp4"
pygame.init()
clock = pygame.time.Clock()

PATH_VID = "C:\\Users\\Home\\Downloads\\nw.mp4"
PATH_AUD = "C:\\Users\\Home\\Downloads\\input_audio.wav"
path_to_static = "C:\\Users\\Home\\.spyder-py3\\Pavel.jpg"


captured = cv2.VideoCapture(PATH_VID)

n = captured.get(cv2.CAP_PROP_FRAME_WIDTH)
m = captured.get(cv2.CAP_PROP_FRAME_HEIGHT)
FPS = captured.get(cv2.CAP_PROP_FPS)
screen = pygame.display.set_mode((n, m))
AUD_done = True
VID_done = True

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
    global VID_done, clock, FPS
    if VID_done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return
        to_show = pygame.image.load(path)
        screen.blit(to_show, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        
            
def play_video_with_sound(path: str, wav_path: str) -> None:
    t1 = threading.Thread(target=play_sd, args=(wav_path,), daemon=True)
    t2 = threading.Thread(target=show_video, args=(path,), daemon=True)
    t2.start()
    t1.start()
    t2.join()
    t1.join()
    while(AUD_done == False or VID_done == False):
        time.sleep(0.01)
        



querries = []
i_q = 0
clock2 = time.time()


events = [5, 25, 30, 70]


while True:
    if len(events) > 0:
        if -clock2 + time.time() > events[0]:
            events.pop(0)
            querries.append([PATH_VID, PATH_AUD])
    if -clock2 + time.time()> 100:
        break
    if(len(querries) == i_q):
        show_static_picture(path_to_static)
        time.sleep(0.02)
    else:
        a = querries[i_q][0]
        b = querries[i_q][1]
        play_video_with_sound(a, b)
        i_q += 1

pygame.quit()