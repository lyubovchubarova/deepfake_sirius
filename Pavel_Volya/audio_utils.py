import speech_recognition
from vosk_tts import Model, Synth
import vosk
import json
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