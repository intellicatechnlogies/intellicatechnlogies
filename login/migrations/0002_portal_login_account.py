from django.db import migrations, models


def copy_existing_portal_accounts(apps, schema_editor):
    LegacyUser = apps.get_model("login", "users")
    PortalLoginAccount = apps.get_model("login", "PortalLoginAccount")
    database = schema_editor.connection.alias

    PortalLoginAccount.objects.using(database).bulk_create(
        [
            PortalLoginAccount(
                username=legacy_user.user_name,
                login_id=legacy_user.login_id,
                password=legacy_user.password,
                is_active=legacy_user.login_active,
                client_name=legacy_user.client_name,
            )
            for legacy_user in LegacyUser.objects.using(database).all().iterator()
        ],
        batch_size=500,
    )


def restore_legacy_credentials(apps, schema_editor):
    LegacyUser = apps.get_model("login", "users")
    PortalLoginAccount = apps.get_model("login", "PortalLoginAccount")
    database = schema_editor.connection.alias

    legacy_users = LegacyUser.objects.using(database)
    for account in PortalLoginAccount.objects.using(database).all().iterator():
        legacy_users.filter(login_id=account.login_id).update(
            password=account.password,
            login_active=account.is_active,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("login", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalLoginAccount",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("username", models.CharField(db_index=True, max_length=150)),
                ("login_id", models.BigIntegerField(blank=True, null=True, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                ("client_name", models.CharField(blank=True, default="", max_length=100)),
            ],
            options={
                "db_table": "portal_login_credentials",
                "ordering": ["username", "id"],
            },
        ),
        migrations.RunPython(copy_existing_portal_accounts, restore_legacy_credentials),
    ]