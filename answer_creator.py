import json  # работа с json-файлами и json-строками
import requests
import yaml
import os
from vosk_tts import Model, Synth

with open('config.yaml') as f:
    var = yaml.load(f, Loader=yaml.FullLoader)

with open('keys.yaml') as f:
    key = yaml.load(f, Loader=yaml.FullLoader)
    
PATH_TO_MODEL = os.getcwd() + var["PATH_TO_MODEL"]
    
class VoiceGenerator:
    def __init__(self):
        self.model = Model(model_path=PATH_TO_MODEL)
    def generate(self, text):
        synth = Synth(self.model)
        path = os.getcwd() + var["PATH_TO_OUTPUT_AUD"]
        synth.synth(text, path)
        return path
    
vg = VoiceGenerator()

def ask(request):
    text = "Я Павел Воля. Люблю рассказывать анекдоты, но еще больше люблю свою жену."
    return vg.generate(text)
    instruction = '''Ответь на запрос так, как ответил бы на него Павел Воля.
            Используй данные из биографии Павла Воли, если это потребуется.
            Отвечай на запрос в его стиле.'''
    #time.sleep(3)

    result = requests.post(
        url=var["answer_serv"],
        headers={
            "Authorization": "Api-Key " + key["answer"],
        },
        json={
            "model": "general",
            "instruction_text": instruction,
            "request_text": request,
            "generation_options": {
                "max_tokens": 60,
                "temperature": 0.5
            }
        }
    )
    data = json.loads(result.text)
    text = data['result']['alternatives'][0]['text']
    vg.generate(text)
    

