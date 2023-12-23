
import json  # работа с json-файлами и json-строками
import os  # работа с файловой системой
import requests
import urllib.request
import pygame
import cv2
import threading
import time
from mutagen.wave import WAVE 
import sys
import yaml

import speech_recognition
from vosk_tts import Model, Synth
import vosk
import wave


class VoiceGenerator:
    def __init__(self, 
                 model_path: str,
                 generated_audio_path: str) -> None:
        
        self.model = Model(model_path=model_path)
        self.synth = Synth(self.model)
        self.generated_audio_path = generated_audio_path
        
    def generate(self, 
                 text: str) -> str:
        '''
        Генерация аудио файнтьюн моделью
        '''
        self.synth.synth(text, self.generated_audio_path)
    
class VoiceRecognizer:
    def __init__(self, 
                recognized_audio_path: str,
                offline_voice_recognition_model_path: str):
        
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()
        self.recognized_audio_path = recognized_audio_path
        self.offline_voice_recognition_model_path = offline_voice_recognition_model_path
    

    def record_audio(self):
        '''
        Подключение к микрофону и запись аудио
        '''
        with self.microphone:

            # регулирование уровня окружающего шума
            self.recognizer.adjust_for_ambient_noise(self.microphone, 
                                                     duration=2)

            try:
                print("Listening...")
                audio = self.recognizer.listen(self.microphone, 5, 5)

                with open(self.recognized_audio_path, "wb") as file:
                    file.write(audio.get_wav_data())
                
                return audio

            except speech_recognition.WaitTimeoutError:
                print("Can you check if your microphone is on, please?")
                return None
            
    def use_offline_recognition(self):
        """
        Переключение на оффлайн-распознавание речи
        :return: распознанная фраза
        """
        recognized_data = ""
        try:
            wave_audio_file = wave.open(self.recognized_audio_path, "rb")
            model = vosk.Model(self.offline_voice_recognition_model_path)
            offline_recognizer = vosk.KaldiRecognizer(model, wave_audio_file.getframerate())

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
            
    def recognize_audio(self):
            audio = self.record_audio()
            if audio:
                try:
                    print("Started recognition...")
                    recognized_data = self.recognizer.recognize_google(audio, language="ru").lower() 
                            
                except speech_recognition.UnknownValueError:
                    pass

                # в случае проблем с доступом в Интернет происходит попытка
                # использовать offline-распознавание через Vosk
                except speech_recognition.RequestError:
                    print("Trying to use offline recognition...")
                    recognized_data = self.use_offline_recognition()
                    return recognized_data

                return recognized_data
            return

#os.environ["REPLICATE_API_TOKEN"] = "r8_68DKrcZ7Tup6Rsw0ATVEggm7cIoGtjs40eUAK"

pygame.init()
clock = pygame.time.Clock()


with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file)
    
with open('keys.yaml') as config_file:
    key = yaml.safe_load(config_file)
    
for key1, val in config["pathes"].items():
    config["pathes"][key1] = os.getcwd() + val

n = 854
m = 480
FPS = 25
screen = pygame.display.set_mode((n, m))


audio_is_ended = True
video_is_ended = True


def play_sound(path_to_audio: str) -> None:
    global audio_is_ended
    audio_is_ended = False
    pygame.mixer.init()
    sounda= pygame.mixer.Sound(path_to_audio)
    sounda.play()
    audio_is_ended = True

def show_video(path: str) -> None:
    global video_is_ended
    video_is_ended = False
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
        
        if not is_ok:
            video_is_ended = True
            return
            
def show_static_picture(path: str = config['pathes']['static_image_path']) -> None:

    global video_is_ended, clock, FPS
    
    if video_is_ended:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        to_show = pygame.image.load(path)
        screen.blit(to_show, (0, 0))
        pygame.display.flip()
        
            
def play_video_with_sound(path: str, 
                          wav_path: str) -> None:
    
    audio_thread = threading.Thread(target=play_sound, args=(wav_path,), daemon=True)
    video_thread = threading.Thread(target=show_video, args=(path,), daemon=True)
    
    video_thread.start()
    audio_thread.start()
    
    video_thread.join()
    audio_thread.join()
    
    while(audio_is_ended == False or video_is_ended == False):
        time.sleep(0.01)


def ask_yagpt(request: str,
              url: str = config['yagpt']['url'],
              instruct: str = config['yagpt']['instruct'],
              model_type: str = config['yagpt']['model_type'],
              max_tokens: int = config['yagpt']['max_tokens'],
              temperature: float = config['yagpt']['temperature']) -> str:
    #return "Я Павел Воля. Привет."
    instruct = "Ответь на запрос так, как ответил бы на него Павел Воля. Используй данные из биографии Павла Воли, если это потребуется. Отвечай на запрос в его стиле. Ответ должен содержать не болеее 5 предложений."
    
    '''
   Отправка запроса в YaGPT. NB! нужно добавить try-except
    '''
    iam_token = key["yagpt"]
    x_folder_id = "b1go14drca6er71a5jpi"
    result = requests.post(
        url='https://llm.api.cloud.yandex.net/llm/v1alpha/instruct',
        headers={'Authorization': f'Bearer {iam_token}', 'x-folder-id': x_folder_id},
        json={
        "model": "general",
        "instruction_text": instruct,
        "request_text": f"{request}\n\n Ответь на вопрос как Павел Воля",
        "generation_options": {
            "max_tokens": 1500,  
            "temperature": 0.5
        }
        }
    )
    data = json.loads(result.text)
    return data["result"]["alternatives"][0]["text"]


if __name__ == "__main__":
    
    # Initialisation
    
    
    querries = []
    iq = 0
    clock2 = time.time()
    
    
    voice_generator = VoiceGenerator(model_path=config['pathes']['voice_generation_model_path'],
                                     generated_audio_path=config['pathes']['generated_audio_path'])
    
    voice_recognizer = VoiceRecognizer(recognized_audio_path=config['pathes']['recognized_audio_path'],
                                       offline_voice_recognition_model_path=config['pathes']['offline_voice_recognition_model_path'])
    
    
    while True:
        
        if(len(querries) == iq):
            show_static_picture()
            time.sleep(0.02)
        else:
            a = querries[iq][0]
            b = querries[iq][1]
            play_video_with_sound(a, b)
            iq += 1
        
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        
        recognized_voice_input = voice_recognizer.recognize_audio()
        print('recognized', recognized_voice_input)
        duration = 101
        while duration > 100:
            voice_generator.generate(ask_yagpt(request = recognized_voice_input))
            
            snd = WAVE(voice_generator.generated_audio_path)
            
            duration = snd.info.length
            
        time.sleep(2)
        
        files = [
            ("input_face", open(config['pathes']['video_sitting_path'], "rb")),
            ("input_audio", open(config['pathes']['generated_audio_path'], "rb")),
        ]
        payload = {}

        response = requests.post(
            "https://api.gooey.ai/v2/Lipsync/form/",
            headers={
                "Authorization": "Bearer " + key["wav2lips"],
            },
            files=files,
            data={"json": json.dumps(payload)},
        )
        assert response.ok, response.content

        result = response.json()
        print(result)
        
        urllib.request.urlretrieve(result['output']['output_video'], 
                                   config['pathes']['generated_video_path'])
        
        querries.append([config['pathes']['generated_video_path'], 
                         config['pathes']['generated_audio_path']])




