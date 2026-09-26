from django.db import migrations


def remove_inactive_portal_accounts(apps, schema_editor):
    PortalLoginAccount = apps.get_model("login", "PortalLoginAccount")
    PortalLoginAccount.objects.using(schema_editor.connection.alias).filter(
        is_active=False
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("login", "0002_portal_login_account"),
    ]

    operations = [
        migrations.RunPython(remove_inactive_portal_accounts, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="portalloginaccount",
            name="client_name",
        ),
        migrations.RemoveField(
            model_name="portalloginaccount",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="portalloginaccount",
            name="login_id",
        ),
    ]