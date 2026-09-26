from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from login.models import users


class Command(BaseCommand):
    help = "Create the development-only demo portal account."

    username = "demo"
    password = "IntellicaDemo!2026"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("The demo account can only be created when DEBUG=True.")

        account = users.objects.filter(user_name__iexact=self.username).order_by("sno").first()
        if account:
            account.password = self.password
            account.login_active = True
            account.save(update_fields=["password", "login_active"])
        else:
            login_id = (users.objects.aggregate(value=Max("login_id"))["value"] or 1901000000) + 1
            users.objects.create(
                client_name="Portal Demo",
                contact_number="",
                state="",
                user_name=self.username,
                user_type="Portal",
                created_date=0,
                email_address="demo@example.com",
                enabled_apis={},
                enabled_services="IDR,CFACE",
                login_id=login_id,
                password=self.password,
                ip_check_flag=False,
                admin_adding=False,
                api_key=None,
                application_quota=500,
                boss_id=1,
                login_active=True,
                office_address="",
                otp_class_flag=False,
                registered_ip_address="0000:0000:0000:0000:0000:0000:0000:0000",
                residential_address="",
                session_active=False,
                session_system_info="",
                session_last_activity_ts=0,
                verticals="",
                created_login_id=login_id,
                otp_count=0,
                reset_password_count=0,
                incorrect_password_count=0,
            )
        self.stdout.write(self.style.SUCCESS("Created or refreshed the development demo portal account."))