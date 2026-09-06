from .errors import check_main_errors
from .env_settings import EnvSettings

env_settings: EnvSettings = EnvSettings(*check_main_errors())