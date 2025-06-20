## API скоринга
***
Цель:

Реализовать логику валидации запросов к API
***
### Инструкция:
Реализовать логику валидации запросов к скоринговому API на базе готового "скелета". Сервис на вход принимает POST запросы с JSON,
содержащий набор атрибутов, требующих проверки на соответсвие набору правил, аналогично тому Django проверяет данные на соответствие
описанию формы. Подразумевается, что реализация будет использовать метаклассы или протокол дескрипторов
***
### Запуск:
Сервер: python api/api.py --port 9084 из корневой директории ДЗ.
### Проверка:
Запросы посредством Postman на http://localhost:9084/method/, например:
- метод POST,
- body JSON вида {"account":"horns&hoofs","login":"admin","method":"clients_interests","token":"4f8add2d761902b09b8bd3084df03ea7d68940d7112dfe50244c0b7f9d3e4eb9b444cc3ff34c881b7662fb7fdf987b221451ee18972e65617ec81f3a4b40b853","arguments":{"client_ids":[1,2,3,4],"date":"20.07.2017"}}

Ответ:
JSON вида {"response": {"1": ["cinema", "tv"], "2": ["geek", "books"], "3": ["books", "sport"], "4": ["otus", "tv"]}, "code": 200}

Тесты локально:  pytest ./api/test.py

pylint --disable=C0103,C0114,C0116,C0115 --fail-under=7 ./api/api.py

black ./api/api.py
