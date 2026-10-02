from django.db import migrations
from django.db.models import Max


def move_portal_accounts(apps, schema_editor):
    PortalAccount = apps.get_model("login", "PortalLoginAccount")
    User = apps.get_model("login", "users")
    database = schema_editor.connection.alias
    next_login_id = (User.objects.using(database).aggregate(value=Max("login_id"))["value"] or 1901000000) + 1

    for account in PortalAccount.objects.using(database).all().iterator():
        user = User.objects.using(database).filter(
            user_name__iexact=account.username
        ).order_by("sno").first()
        if user:
            user.password = account.password
            user.login_active = True
            user.save(using=database, update_fields=["password", "login_active"])
            continue

        User.objects.using(database).create(
            client_name="Portal",
            contact_number="",
            state="",
            user_name=account.username,
            user_type="Portal",
            created_date=0,
            email_address="example@example.com",
            enabled_apis={},
            enabled_services="IDR,CFACE",
            login_id=next_login_id,
            password=account.password,
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
            created_login_id=next_login_id,
            otp_count=0,
            reset_password_count=0,
            incorrect_password_count=0,
        )
        next_login_id += 1


class Migration(migrations.Migration):
    dependencies = [
        ("login", "0003_portal_credentials_only"),
    ]

    operations = [
        migrations.RunPython(move_portal_accounts, migrations.RunPython.noop),
        migrations.DeleteModel(name="PortalLoginAccount"),
    ]