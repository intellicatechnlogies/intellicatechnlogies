from getpass import getpass

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from login.models import users


class Command(BaseCommand):
    help = "Create an interactive portal login account (separate from API credentials)."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Plaintext portal passwords are allowed only when DEBUG=True.")

        username = options["username"].strip()
        if not username:
            raise CommandError("Username cannot be empty.")
        if users.objects.filter(user_name__iexact=username).exists():
            raise CommandError("A portal account with this username already exists.")

        password = getpass("Password: ")
        confirmation = getpass("Confirm password: ")
        if not password:
            raise CommandError("Password cannot be empty.")
        if password != confirmation:
            raise CommandError("Passwords do not match.")
        login_id = (users.objects.aggregate(value=Max("login_id"))["value"] or 1901000000) + 1
        users.objects.create(
            client_name="Portal",
            contact_number="",
            state="",
            user_name=username,
            user_type="Portal",
            created_date=0,
            email_address="example@example.com",
            enabled_apis={},
            enabled_services="IDR,CFACE",
            login_id=login_id,
            password=password,
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
        self.stdout.write(self.style.SUCCESS(f"Portal account '{username}' created."))