\#Main.py

Перед тем как запускать main.py нужно:



1. python -m pip install --upgrade pip - обновит установщик пакетов pip



2\. pip install -r requirements.txt - установит библиотеки для работы приложения



3\. Запустить из файла main.py приложение



После этих действий запустится fastapi swagger, поидее, по ссылке http://localhost:8000/docs, можно будет перейти к нему







\#DOCKER

Установить Docker desktop



Запустить Docker desktop, убедиться что движок запущен



docker build --no-cache -t ml\_service . - Сбилдить образ контейнера



docker run -p 8000:8000 --name ml\_service\_container ml\_service - развернуть контейнер из образа



\#О скриптах



Есть 2 скрипта



1. download\_model.py - Находится в app/scripts/, загружает модель YOLO8, просто типо на комп грузит модельку. чтобы она локально у тебя была

2\. upload\_container\_images.ps1 - Этот скрипт нужен для того, чтобы выгружать из контейнера docker, результаты, типо изображения с баундин боксами. Он используется только при запущенном контейнере. Просто вытягивает результаты, создавая в проекте папку results\_container.



ВАЖНО Запускается при помощи другого файла: start\_upload\_container.bat

