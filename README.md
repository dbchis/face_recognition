setting
## 1 pip install virtualenv
## 2 virtualenv venv
## 3 venv\Scripts\activate
## 4 pip install -r requirements.txt
run
## 1 venv\Scripts\activate
## 2 py bot.py


note
## 3.11.5
## pip install virtualenv
## virtualenv venv
## venv\Scripts\activate
Set-ExecutionPolicy RemoteSigned
## pip install -r requirements.txt
## pip freeze > requirements.txt
## deactivate
pyinstaller --onefile --add-data "img:img" --add-data "library:library" --add-data "data:data" --add-data "models:facenet_pytorch/data" --add-data "commands.json:." --add-data "face_recognition.py:." bot.py
pyinstaller --onefile --noconsole --add-data "models:facenet_pytorch/data" verify.py 

