from django.apps import AppConfig


class SocialappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialapp'
    
    def ready(self):
        """Initialize signals when app is ready"""
        import socialapp.signals  # noqa
