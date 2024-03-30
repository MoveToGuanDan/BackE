from django.apps import AppConfig
import threading
from .MatchMaking import match_making


class MatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Match'

    def ready(self):
        # 确保只在主线程中启动守护线程，避免自动重载器导致的重复启动
        if threading.current_thread() is threading.main_thread():
            thread = threading.Thread(target=match_making, daemon=True)
            thread.start()




