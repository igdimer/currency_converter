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

Linters and tests: isort, flake8, mypy, pytest.

### API

There is an endpoint for obtaining exchange rates.

```GET /api/rate?base=USD&target=EUR```

Query parameters ```base``` and ```target``` are required and must be represented by a widely recognized three-letter alphabetical code.

Documentation is available on http://127.0.0.1:8000/docs.

***The project is evolving, new features are coming soon.***

### Launch project

If you'd like to launch project on your own machine, after cloning repository you should follow the next steps:

- Get access key on https://exchangerate.host/
- Set environment variable EXCHANGERATE_ACCESS_KEY to obtained access key in file ```env.example``` (or you can set it in file ```.env``` inside the container ```web``` after docker run)
- Run ```docker-compose up```
- Inside the container ```web``` execute command ```alembic upgrade head```
 