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

PATH_TO_MODEL = "C:/Users/user/Desktop/deepfake_sirius/Model"
PATH_TO_OUTPUT = "C:/Users/user/Desktop/deepfake_sirius/materials/audio"


k = "sk-YOVNQzHmpga9My3dwlSo9BQN907TuPZQXcHn50ztigTwm3I2"
files = [
    ("input_face", open("C:\\Users\\user\\Desktop\\deepfake_sirius\\materials\\scale_1200.jpg", "rb")),
    ("input_audio", open("C:\\Users\\user\\Desktop\\deepfake_sirius\\materials\\audio\\output.wav", "rb")),
]
payload = {}


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
    Ответь на запрос так, как ответил бы на него Павел Воля. Используй данные из биографии Павла Воли, если это потребуется. Отвечай на запрос в его стиле. Ответ должен содержать не болеее 10 предложений.
    """

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

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    vg = VoiceGenerator()
    while True:
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(voice_input)
        path_to_file = vg.generate(ask(voice_input))
        print(path_to_file)
        response = requests.post(
            "https://api.gooey.ai/v2/Lipsync/form/",
            headers={
                "Authorization": "Bearer " + k,
            },
            files=files,
            data={"json": json.dumps(payload)},
        )
        assert response.ok, response.content
        #song = AudioSegment.from_wav(path_to_file)
        result = response.json()
        print(response.status_code, result["output"]["output_video"])
        #play(song)
        urllib.request.urlretrieve(result["output"]["output_video"], "C:\\Users\\user\\Desktop\\deepfake_sirius\\materials\\video.mp4")
        os.startfile("C:\\Users\\user\\Desktop\\deepfake_sirius\\materials\\video.mp4")
        break;




