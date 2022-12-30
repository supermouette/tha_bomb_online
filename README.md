# Tha Bomb online : legit.engineer

This is the code of [legit.engineer](https://legit.engineer)
The main part of this website is to host an online version of the game time bomb

# How to install locally

- clone the project
- make sure you have python 3.11 installed
- Install the requirements : ```pip install -r requirements.txt```
- set correctly timebomb/settings.py :
  - you can comment HTTPS settings
  - set DEBUG to True
  - change the database settings to your own one, the most simple one is :
    ```
    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
      }
    }
    ```
   - set a secret key
   - comment out the last line of the file
  - init the db with : ```python manage.py migrate```
  - start the server : ```python manage.py runserver```
