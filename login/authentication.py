"""Authentication helpers for portal and API account stores."""

from django.contrib.auth.hashers import check_password
from django.utils.crypto import constant_time_compare

from login.managers import LEGACY_PASSWORD_SALT, get_hash
from login.models import users


def get_user_for_login(identity):
    """Find an active interactive account in the existing login_users table."""
    if not identity:
        return None

    identity = str(identity).strip()
    if not identity:
        return None

    if identity.isdecimal():
        user = users.objects.filter(login_id=int(identity), login_active=True).first()
        if user:
            return user

    matches = users.objects.filter(user_name__iexact=identity, login_active=True)
    if matches.count() == 1:
        return matches.first()
    return None


def get_api_user_for_login(identity):
    """Look up credentials in the legacy account table for API authentication."""
    if not identity:
        return None

    identity = str(identity).strip()
    if not identity:
        return None

    if identity.isdecimal():
        user = users.objects.filter(login_id=int(identity)).first()
        if user:
            return user

    matches = users.objects.filter(user_name__iexact=identity)
    if matches.count() == 1:
        return matches.first()
    return None


def verify_user_password(user, raw_password):
    """Verify credentials and upgrade legacy password formats on success."""
    if not raw_password or not user.login_active:
        return False

    stored_password = user.password or ""
    try:
        valid_password = check_password(raw_password, stored_password)
    except ValueError:
        valid_password = False

    # Older accounts may contain plaintext passwords or the application's
    # former deterministic Argon2 digest. Never write either format again.
    if not valid_password:
        if constant_time_compare(raw_password, stored_password):
            valid_password = True
        elif len(stored_password) == 128:
            legacy_digest = get_hash(raw_password, LEGACY_PASSWORD_SALT)
            valid_password = constant_time_compare(legacy_digest, stored_password)

    return valid_password
