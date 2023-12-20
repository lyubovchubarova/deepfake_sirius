from vosk_tts import Model, Synth
import os.path

PATH_TO_MODEL = "/vosk-model-tts-ru-0.4-multi"
PATH_TO_OUTPUT = "/"


class VoiceGenerator:
    def __init__(self):
        self.model = Model(model_path=PATH_TO_MODEL)

    def generate(self, text, file_name):
        synth = Synth(self.model)
        path = os.path.join(PATH_TO_OUTPUT, file_name)
        synth.synth(text, path)
        return path
