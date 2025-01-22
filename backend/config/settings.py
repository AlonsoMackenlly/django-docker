from os import environ

environ.setdefault("DJANGO_ENV", "development")

DJANGO_ENV = environ["DJANGO_ENV"]

if DJANGO_ENV in ["local", "development"]:
    pass
elif DJANGO_ENV == "production":
    pass
