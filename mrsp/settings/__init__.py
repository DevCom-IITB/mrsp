from decouple import config

try:
    ENV = config("ENV", default="production")
except Exception:
    ENV = "development"

if ENV == "development":
    from .development import *

else:
    from .production import *