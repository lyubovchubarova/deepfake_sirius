# deepfake_sirius

## Краткое описание проекта

## Vosk voice cloning finetune

Дообучали модель с опорой на [инструкцию от vosk для voice cloning](https://github.com/alphacep/vosk-tts/blob/master/training/README.md) на русскоязычной модели. Собрали много ошибок по пути, полная инструкция с процессом обучения в `voicecloning_russian_tutorial.ipynb`.

Датасет [здесь](https://drive.google.com/drive/folders/1rBujDC7qd-J8cEoDoEkQLRd9UQiSQibs)


## Запуск приложения

Сначала необходимо скачать папку Pavel_Volya на компьютер

```
!git clone https://github.com/lyubovchubarova/deepfake_sirius.git
```

Далее нужно установить все библиотеки для Python из Pavel_Volya/requirements.txt
```
pip install -r requirements.txt
```

Нужно скачать модели распознавания речи и модель синтеза: в папку Pavel_Volya добавить папки recognizer_vosk_small_ru и vosk-volya-finetuned. Эти папки находятся по [ссылке](https://drive.google.com/drive/folders/1Ja39dDZW96ijZqNfMAh93VcE7gFO5NYr?usp=sharing)

В файл keys.yaml нужно вставить ключи API для yagpt и для модели wav2lip. Запустите файл main.py

Готово!
