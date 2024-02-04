# Currency converter

API for obtaining currency exchange rates. Service uses external API https://exchangerate.host/.

### Stack

- Python 3.11
- FastAPI 0.104
- SQLAlchemy 2.0
- PostgreSQL
- Redis
- Docker
- alembic
- httpx

Linters and tests: isort, flake8, mypy, pytest.

### API

#### Registration and authentication

```POST /api/signup``` - sign up as new user and get JWT access and refresh tokens

_Request body JSON_

```json
{
  "username": "your_username",
  "password": "secure_password"
}
```

```POST /api/login``` - log in by username and password and get JWT access and refresh tokens

_Request body JSON_

```json
{
  "username": "your_username",
  "password": "secure_password"
}
```

```POST /api/refresh_token``` - get new access token by refresh token

_Request body JSON_

```json
{
  "refresh_token": "your_jwt_refresh_token"
}
```

#### Currencies

```GET /api/rate?base=USD&target=EUR``` - obtain exchange rates

Query parameters ```base``` and ```target``` are required and must be represented by a widely recognized three-letter alphabetical code.

```POST /api/favorite_rates``` - create list of favorite currency pairs

_Authorization Header: Bearer <jwt_access_token>_

_Request body JSON_

```json
{
  "pairs": [
    {
        "base": "RUB",
        "target": "EUR"
    },
    {
        "base": "USD",
        "target": "BTC"
    }
  ]
}
```

```GET /api/favorite_rates``` - get currency rates from favorite list

_Authorization Header: Bearer <jwt_access_token>_

Documentation is available on http://127.0.0.1:8000/docs.

***The project is evolving, new features are coming soon.***

### Launch project

If you'd like to launch project on your own machine, after cloning repository you should follow the next steps:

- Get access key on https://exchangerate.host/
- Set environment variable EXCHANGERATE_ACCESS_KEY to obtained access key in file ```env.example``` (or you can set it in file ```.env``` inside the container ```web``` after docker run)
- Run ```docker-compose up```
- Inside the container ```web``` execute command ```alembic upgrade head```
 