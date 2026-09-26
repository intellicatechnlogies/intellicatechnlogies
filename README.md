
# Intellica Technologies

Django application configured for Gunicorn behind Nginx. WhiteNoise serves the
collected, compressed, fingerprinted CSS, JavaScript, and image assets; Nginx
proxies application requests to Gunicorn.

## Local development

1. Create and activate a Python virtual environment, then install `requirements.txt`.
2. Copy `.env.example` to `.env` (the repository includes local-only defaults).
3. Run `python manage.py migrate` and `python manage.py runserver`.

The local `.env` is ignored by Git. Its development key must not be used in
production.

## GCP deployment (existing Gunicorn/Nginx VM, SQLite)

This deployment uses the server's existing Gunicorn and Nginx installation; it
does not require Docker. Django uses SQLite by default and WhiteNoise serves the
collected static files through Gunicorn/Nginx.

1. Back up the existing `db.sqlite3` before deploying. Keep the database on
	persistent VM storage, not a temporary directory. If you move it outside the
	application directory, set `DB_NAME` to its absolute path and ensure the
	Gunicorn service account can read and write the database and its parent
	directory. Do not check the database into Git.
2. Set the production environment for the existing Gunicorn service:
	`DJANGO_DEBUG=False`, a strong unique `DJANGO_SECRET_KEY`, the real
	`DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS`. Set
	`DB_ENGINE=sqlite3`, and optionally `DB_NAME=/var/lib/intellica/db.sqlite3`.
	Supply secrets through the server's secret/environment mechanism, not source
	control. Leave HSTS disabled until HTTPS is fully verified.
3. From the application directory and its virtual environment, install the
	requirements, run `python manage.py migrate`, then run
	`python manage.py collectstatic --noinput`. The production static manifest is
	generated in `staticfiles/`; WhiteNoise serves it, so an Nginx static alias is
	not required. Ensure the Gunicorn process can read `staticfiles/`.
4. Update the existing Gunicorn service to use the application's virtual
	environment, application directory, production environment variables, and
	`IntellicaTechnologies.wsgi:application`; then restart that service. Keep
	Gunicorn bound to loopback or a Unix socket, not a public interface.
5. Keep Nginx proxying application requests to the existing Gunicorn listener.
	Use `deploy/nginx.conf.example` as a reference, not a replacement for the
	server's current configuration. Allow uploads up to at least 80 MiB for
	multi-image face comparisons. Forward the correct `Host`, client IP, and
	HTTPS scheme; if Nginx terminates TLS itself, forward `$scheme` as
	`X-Forwarded-Proto`. Verify the home page, login, and `/static/` assets over
	HTTPS after restarting.

SQLite is appropriate for a single VM and modest write concurrency. Begin with
one Gunicorn worker, keep a tested backup/restore procedure, and monitor for
`database is locked` errors before increasing worker count. If write traffic or
availability requirements grow, migrate to a server database rather than
running SQLite across multiple instances.

Before release, run `python manage.py check --deploy` with the production
environment and review the security warnings.
