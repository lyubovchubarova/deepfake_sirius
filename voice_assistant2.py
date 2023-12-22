from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import wave  # создание и чтение аудиофайлов формата wav
import json  # работа с json-файлами и json-строками
import os  # работа с файловой системой
import requests
import json
from vosk_tts import Model, Synth
import IPython
from pydub import AudioSegment
from pydub.playback import play
import urllib.request
import pygame
import cv2
import winsound
import threading
import time
from mutagen.wave import WAVE 
import sys
import replicate

os.environ["REPLICATE_API_TOKEN"] = "r8_CFK39V3LwnMsLBOHqqSHgzbPnWMDyun4ITC23"

PATH_TO_MODEL = "C:/Users/Home/.spyder-py3/PROJECT/deepfake_sirius/Model"
PATH_TO_OUTPUT = "C:/Users/Home/.spyder-py3/PROJECT/deepfake_sirius/materials/audio"
pygame.init()
clock = pygame.time.Clock()

PATH_VID = "C:\\Users\\Home\\.spyder-py3\\PROJECT\\deepfake_sirius\\materials\\video.mp4"
PATH_AUD = "C:/Users/Home/.spyder-py3/PROJECT/deepfake_sirius\\materials\\audio\\output.wav"
path_to_static = "C:\\Users\\Home\\.spyder-py3\\Pavel.jpg"


k = ["sk-YOVNQzHmpga9My3dwlSo9BQN907TuPZQXcHn50ztigTwm3I2",
     "sk-DKWviaouOyORNe99POfuCgagQp53fpkYa1fNMkpvS65MuPnh", 
     "sk-TDOHxwdu7FBLHzXacsBJwnbM8Q8sOicd7iRSQg3WIodWFmrt",
     "sk-jhQuijopgd1jw7N3Pk5KkmxZQSscotqMpX44q8dsWvwsECNo",
     "sk-bBSX9yuOPJfZILCnOE3SP6o725APm1TkDgvJxLQhH9m5d2xc",
     "sk-V4YSLuVPQIAwVTCnhcgRGU3jo3rww7PhRVVlSXHfZ01ibWAL",
     "sk-MbIIHo5SbxpNFoh3KtcEVnOp4LldB3QO2SjkflSco0hCH3ib",
     "sk-tyEfquscRrcOVHYDGpNcYI6Gb5ukhWjj1vynGti6m0npXtI0",
     "sk-SZE1yyVsIl7WxQttIlHxDWnXEgiAyLztnblAkRqAfpjIYGRe",
     "sk-TRXxEGmQSBF2v24BUUr1PDFTi6QeZ0m46bZDiv4uGCMp6Woz"]
ik = 0

files = [
    ("input_face", open(path_to_static, "rb")),
    ("input_audio", open(PATH_AUD, "rb")),
]
payload = {}


n = 640
m = 480
FPS = 25
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


class VoiceGenerator:
    def __init__(self):
        self.model = Model(model_path=PATH_TO_MODEL)
    def generate(self, text):
        synth = Synth(self.model)
        path = PATH_TO_OUTPUT + "/output.wav"
        synth.synth(text, path)
        return path

def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        # использование online-распознавания через Google
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит попытка
        # использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data

def ask(request):
    instruction = """
    Ответь на запрос так, как ответил бы на него Павел Воля. Используй данные из биографии Павла Воли, если это потребуется. Отвечай на запрос в его стиле. Ответ должен содержать не болеее 5 предложений.
    """
    #time.sleep(3)

    result = requests.post(
        url='https://llm.api.cloud.yandex.net/llm/v1alpha/instruct',
        headers={
            "Authorization": "Api-Key AQVNyVqBi-XoJ1cAo7VIxq6ztgXm3owqowtso5Qb",
        },
        json={
            "model": "general",
            "instruction_text": instruction,
            "request_text": request,
            "generation_options": {
                "max_tokens": 1500,
                "temperature": 0.5
            }
        }
    )
    data = json.loads(result.text)
    return(data['result']['alternatives'][0]['text'])



if __name__ == "__main__":
    querries = []
    iq = 0
    clock2 = time.time()
    

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    vg = VoiceGenerator()
    
    
    while True:
        
        if(len(querries) == iq):
            show_static_picture(path_to_static)
            time.sleep(0.02)
        else:
            a = querries[iq][0]
            b = querries[iq][1]
            play_video_with_sound(a, b)
            #show_static_picture(path_to_static)
            #time.sleep(0.02)
            iq += 1
        
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(voice_input)
        duration = 101
        while duration > 100:
            path_to_file = vg.generate(ask(voice_input))
            print(path_to_file)
            snd = WAVE(path_to_file)
            duration = snd.info.length
            
        #time.sleep(3)
        output = replicate.run(
            "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
            input={"face": open(path_to_static, "rb"),
                  "audio": open(PATH_AUD, "rb")}
        )
        print(output)

        #play(song)
        urllib.request.urlretrieve(output, PATH_VID)
        querries.append([PATH_VID, PATH_AUD])
        #os.startfile(PATH_VID)
        #break;
        




