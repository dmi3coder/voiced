# Voiced

## About

I put a hard deadline of 2 hours for this project. Obviously it's not what you'd put in production, especially because
following reasons:

1. Docker, Terraform, K8s/kubeless setup is missing
2. CI is missing
3. No tests
4. No caching
5. No secrets management(I faked it with `config.py`)
6. No proper logging
7. Cronjob would be better with a K8s cronjob
8. Auth is not secure - needs proper Oauth2
9. Checks on indexes were not done - so most likely data is not indexed properly
10. No OpenAPI setup - crucial for frontend communication
11. Some logic from controllers(auth, follow) should be extracted into Services

### Structure

1. `main.py` - FastAPI app
2. `voiced/config.py` - Config file
3. `voiced/model/dto` - Pydantic models(DTO)
4. `voiced/model` - SQLAlchemy models
5. `voiced/service` - Services(for now only reports but in real world where core logic will lay)
6. `voiced/controller` - REST-Controllers
7. `alembic` - Migrations

## Setup

```shell
docker-compose up -d
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Run the cronjob

The command will run the cronjob every 5 minutes with results of followers from each user in the database.

Don't forget venv.

```shell
celery -A voiced.service.reports  worker --loglevel=info -B
```

## Test API calls

### Register first user:

```shell
curl --location --request POST 'localhost:8000/register' --header 'Content-Type: application/json' \
--data-raw '{
    "username": "dmytro",
    "email": "dmytro@gmail.com",
    "password": "$Testtest22"
}'
```

### Register second user


```shell
curl --location --request POST 'localhost:8000/register' --header 'Content-Type: application/json' \
--data-raw '{
    "username": "ivan",
    "email": "ivan@gmail.com",
    "password": "$Testtest33"
}'
```

### Login:

```shell
export ACCESS_TOKEN=$(curl --location --request POST 'localhost:8000/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "dmytro",
    "password": "$Testtest22"
}' | jq -r '.access_token')
echo $ACCESS_TOKEN
```

### Info about you:

P.S password is visible, in real app we'll have probably a `profile` for visible and `user` for private info.

```shell
curl --location --request GET 'localhost:8000/me/' \
--header "Authorization: Bearer ${ACCESS_TOKEN}"
```

### Info about followers
In real world that'll be an endpoint you call when you open your profile.

```shell
curl --location --request GET 'localhost:8000/me/details' \
--header "Authorization: Bearer ${ACCESS_TOKEN}"
```

### Follow someone

`username` is a name of second user

```shell
 curl --location --request POST 'localhost:8000/user/ivan/follow' --header "Authorization: Bearer ${ACCESS_TOKEN}"
```

Check celery, it should show amount of followers for as 1 -> ivan

### Unfollow someone

`username` is a name of second user

```shell
 curl --location --request DELETE 'localhost:8000/user/ivan/unfollow' --header "Authorization: Bearer ${ACCESS_TOKEN}"
```