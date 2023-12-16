# Flask-SQL

Esta aplicación muestra un ejemplo de usar Flask SQL Alchemy para crear una base de datos y hacer consultas a la misma.

## Instalación

Para instalar las dependencias del proyecto, ejecutar el siguiente comando:

```bash
pip install -r requirements.txt
```

Ahora instale las dependencias de docker:

```bash
docker-compose up -p flask-sql -d
```

## Uso

1. Cree un archivo `.env` con las siguientes variables de entorno:

    ```bash
    FLASK_APP=main.py
    SECRET_KEY=change-me
    API_ADMIN_USERNAME=admin
    API_ADMIN_PASSWORD=admin
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=flask_test
    PGADMIN_DEFAULT_EMAIL=admin@admin.com
    PGADMIN_DEFAULT_PASSWORD=admin
    ```

2. Ahora ejecute el siguiente comando para inicializar la aplicación:

    ```bash
    flask deploy
    ```

3. Ahora puede ejecutar la aplicación con el siguiente comando:

    ```bash
    flask run
    ```


