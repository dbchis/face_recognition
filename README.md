
## pip install virtualenv
## venv\Scripts\activate
## Set-ExecutionPolicy RemoteSigned
## pip install -r requirements.txt
## pip freeze > requirements.txt
## deactivate
## hehe
pyinstaller --onefile --add-data "img:img" --add-data "library:library" --add-data "data:data" --add-data "models:facenet_pytorch/data" bot.py
