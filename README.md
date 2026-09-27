
# Intellica Technologies

Django application configured for Gunicorn behind Nginx. WhiteNoise serves the
collected, compressed, fingerprinted CSS, JavaScript, and image assets; Nginx
proxies application requests to Gunicorn.

## Local development

1. Create and activate a Python virtual environment, then install `requirements.txt`.
2. Run `python manage.py migrate` and `python manage.py runserver`.

Settings are fixed in `IntellicaTechnologies/settings.py`; no `.env` file or
environment-variable setup is required. Local and production use SQLite at
`db.sqlite3` and the same host/origin allowlists. The production load balancer
must terminate HTTPS. Update the source settings directly if the deployment
domain or database location changes.

## GCP deployment (existing Gunicorn/Nginx VM, SQLite)

This deployment uses the server's existing Gunicorn and Nginx installation; it
does not require Docker. Django uses SQLite by default and WhiteNoise serves the
collected static files through Gunicorn/Nginx.

1. Back up the existing `db.sqlite3` before deploying. Keep the database on
	persistent VM storage, not a temporary directory. The fixed database path is
	`db.sqlite3` in the application directory; ensure the Gunicorn service
	account can read and write it. Do not check the database into Git.
2. No environment variables or `.env` file are required. Keep the production
	load balancer configured for HTTPS and forward the correct `Host`, client IP,
	and HTTPS scheme.
3. From the application directory and its virtual environment, install the
	requirements, run `python manage.py migrate`, then run
	`python manage.py collectstatic --noinput`. The production static manifest is
	generated in `staticfiles/`; WhiteNoise serves it, so an Nginx static alias is
	not required. Ensure the Gunicorn process can read `staticfiles/`.
4. Update the existing Gunicorn service to use the application's virtual
	environment, application directory, and
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

Before release, run `python manage.py check --deploy` and review the security
warnings. This no-environment configuration uses a source-defined Django
signing key and does not mark cookies as HTTPS-only so local HTTP testing
works; these choices are less secure than deployment-specific secrets and
secure-cookie settings.
