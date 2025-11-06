# Tha Bomb online : legit.engineer

This is the code of [legit.engineer](https://legit.engineer)
The main part of this website is to host an online version of the game time bomb

# How to install locally

- clone the project
- make sure you have uv installed
- ```uv venv``` to create a virtual env
- ```uv sync``` to install the dependencies
- set up a `.env` file by coping .env.exemple and set up a secret key
- init the db with : ```uv run python manage.py migrate```
- start the server : ```uv run python manage.py runserver```
