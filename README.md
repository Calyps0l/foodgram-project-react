![workflow](https://github.com/Calyps0l/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Продуктовый помощник Foodgram
## Описание
Foodgram - это сайт, позволяющий пользователям публиковать рецепты, добавлять чужие рецепты в избранное, подписываться 
на публикации других авторов, а также скачивать список продуктов, необходимых для приготовления выбранных блюд.
## Запуск проекта (локально и с помощью Docker)
### Запускаем проект локально
Клонируем репозиторий
```
git clone git@github.com:Calyps0l/foodgram-project-react.git
cd foodgram-project-react
```
Создаем и активируем виртуальное окружение
```
python -m venv venv
source venv/Scripts/activate
```
Устанавливаем зависимости
```
cd backend
python -m pip install -r requirements.txt
```
Выполняем миграции
```
python manage.py makemigrations  
python manage.py migrate
```
Импортируем ингредиенты и тэги
```
python manage.py load_ingr  
python manage.py load_tag  
```
При необходимости создаем суперпользователя
```
python manage.py createsuperuser    
```
Запускаем проект
```
python manage.py runserver    
```
### Запускаем проект через Docker
Клонируем репозиторий
```
git clone git@github.com:Calyps0l/foodgram-project-react.git
cd foodgram-project-react
```
Переходим в infra
```
cd infra
```
Собираем контейнеры
```
docker-compose up -d --build 
```
Выполняем миграции
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate 
```
Загружаем статику
```
docker-compose exec backend python manage.py collectstatic --noinput
```
Импортируем ингредиенты и тэги
```
docker-compose exec backend python manage.py load_ingr
docker-compose exec backend python manage.py load_tag 
```
При необходимости создаем суперпользователя
```
docker-compose exec backend python manage.py createsuperuser  
```
После запуска контейнеров API документация будет доступна по адресу: http://localhost/api/docs/
