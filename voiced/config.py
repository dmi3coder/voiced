import os
# IN real application proper yaml config structure should be used:
# application.yml
# application-dev.yml
# application-prod.yml...
# For simplicity, I will use python file to store configuration

config = {
    "db": {
        "user": os.getenv("DB_USER", "voiced"),
        "password": os.getenv("DB_PASSWORD", "voiced"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5499"),
        "name": os.getenv("DB_NAME", "voiced"),
    }
}