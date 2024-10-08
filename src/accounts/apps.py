import os
from django.apps import AppConfig
from django.conf import settings

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        self.configure_social_apps()

    def configure_social_apps(self):

        def create_social_app(provider, name, client_id, secret_key):
            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
            from dotenv import load_dotenv, set_key

            site, _ = Site.objects.get_or_create(
                domain=os.getenv('domain','http://127.0.0.1:8000'),
                defaults={'name': os.getenv('domain_name', 'http://127.0.0.1:8000')}
            )

            site.save()
            settings.SITE_ID = site.id

            # Path to your .env file
            load_dotenv()
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env') # pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long
            set_key(env_file, 'SITE_ID', str(site.id)) # Write or update SITE_ID

            app, created = SocialApp.objects.get_or_create(provider=provider, name=name)
            app.client_id = client_id
            app.secret = secret_key
            app.sites.add(site)
            app.save()

        # Example: Add Google provider
        create_social_app(
            provider='google',
            name='google',
            client_id=os.getenv('client_id'),
            secret_key=os.getenv('secret_key'),
        )
