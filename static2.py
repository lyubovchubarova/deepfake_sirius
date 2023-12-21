import pygame
import cv2
import winsound
import threading
import time
#"C:\Users\Home\Downloads\nw.mp4"


captured = cv2.VideoCapture("C:\\Users\\Home\\Downloads\\nw.mp4")

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
    clock = pygame.time.Clock()
    
    while(is_ok):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                VID_done = True
                return
                #is_ok = False
        is_ok, vid = captured.read()
        if is_ok:
            to_show = pygame.image.frombuffer(vid.tobytes(), vid.shape[1::-1], "BGR")
        screen.blit(to_show, (0, 0))
        pygame.display.flip()
        
        if is_ok == False:
            VID_done = True
            return
            captured = cv2.VideoCapture("C:\\Users\\Home\\Downloads\\nw.mp4")
            is_ok, vid = captured.read()
            
def play_video_with_sound(path: str, wav_path: str) -> None:
    t1 = threading.Thread(target=play_sd, args=(wav_path,), daemon=True)
    t2 = threading.Thread(target=show_video, args=(path,), daemon=True)
    t2.start()
    t1.start()
    t2.join()
    t1.join()
    while(AUD_done == False or VID_done == False):
        time.sleep(0.01)

play_video_with_sound("C:\\Users\\Home\\Downloads\\nw.mp4", 
           "C:\\Users\\Home\\Downloads\\input_audio.wav")

pygame.quit()