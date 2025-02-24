
## Пошаговый roadmap для создания и настройки Django-проекта с использованием базы данных PostgreSQL, до момента заполнения таблиц:

1. Создание виртуального окружения
Установить Python.
Создайть виртуальное окружение:
```python -m venv venv```
Активировать виртуальное окружение:
Linux/macOS:
```source venv/bin/activate```
Windows:
```venv\Scripts\activate```

2. Установить Django и необходимые библиотеки
Установить Django и psycopg2 (для работы с PostgreSQL):
```pip install django psycopg2-binary```
Создайть файл requirements.txt для сохранения зависимостей:
```pip freeze > requirements.txt```

-- Вот в этом моменте нужно создать локальный гит-репозиторий, репозиторий на github и связать их.
Сформировать .gitiignore и сделать первый коммит
Затем сразу создать ветку develop и дальнейшую разработку вести в ней.

3. Создание нового Django-проекта
Создайть проект с помощью команды:
```django-admin startproject myproject .```
   (здесь myproject — имя проекта),
или
```django-admin startproject config .```

Проверь, что проект корректно создан, выполнив команду:
```python manage.py runserver```

4. Настройка подключения к PostgreSQL
Установить PostgreSQL (если еще не установлен).
Создайть базу данных и пользователя PostgreSQL:
```
CREATE DATABASE myprojectdb;
CREATE USER myprojectuser WITH PASSWORD 'password';
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE myprojectdb TO myprojectuser;
Измените настройки базы данных в файле settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myprojectdb',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Создание приложения
Создайть новое приложение:
```python manage.py startapp myapp```
Зарегистрировать приложение в INSTALLED_APPS (в файле settings.py):
```
INSTALLED_APPS = [
    ...
    'myapp',
]
```

6. Создание моделей
Открыть файл models.py в приложении myapp и создать необходимые модели. Например:
```
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateField()
```

7. Применение миграций
Сгенерировать файлы миграций для базы данных:
python manage.py makemigrations
Применить миграции для создания таблиц в базе данных:
```python manage.py migrate```

8. Создание суперпользователя
Создайть суперпользователя для админ-панели:
```python manage.py createsuperuser```
Ввести имя пользователя, email и пароль.

9. Доступ к админ-панели
Добавить модели в админ-панель, чтобы их можно было редактировать:
В файле admin.py приложения myapp:
```
from django.contrib import admin
from .models import Author, Book

admin.site.register(Author)
admin.site.register(Book)
```
Запустить сервер:
```python manage.py runserver```
Перейти по адресу http://127.0.0.1:8000/admin/ и войти с учетными данными суперпользователя.

10. Заполнение таблиц
Использовать админ-панель или создать данные с помощью Django ORM:
```
from myapp.models import Author, Book

author = Author.objects.create(name="John Doe", email="john.doe@example.com")
Book.objects.create(title="Django Basics", author=author, published_date="2025-01-01")
```
После этих шагов будет готовый Django-проект с таблицами в базе данных PostgreSQL, готовыми к заполнению и использованию.
