import base64
import json
from io import StringIO
from unittest.mock import patch

from django.apps import apps
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from login.authentication import get_api_user_for_login, get_user_for_login
from login.managers import LEGACY_PASSWORD_SALT, get_hash
from login.models import users
from Services.models import service_result, transactions_log


class LoginViewTests(TestCase):
    def create_user(self, password="plain-password", **overrides):
        values = {
            "client_name": "Test Client",
            "contact_number": "1234567890",
            "state": "Test State",
            "user_name": "testuser",
            "user_type": "Executive",
            "created_date": 0,
            "login_id": 1901000001,
            "password": password,
            "login_active": True,
            "office_address": "Test office",
            "residential_address": "Test residence",
            "session_system_info": "",
            "verticals": "",
        }
        values.update(overrides)
        return users.objects.create(**values)

    def post_login(self, identity, password, captcha_answer=None, **extra):
        self.client.get("/login")
        if captcha_answer is None:
            captcha_answer = self.client.session["login_captcha_answer"]
        return self.client.post(
            "/login",
            {
                "loginid": identity,
                "psw": password,
                "captcha_answer": captcha_answer,
                **extra,
            },
        )

    def test_login_table_is_existing_login_users_model(self):
        self.assertEqual(users._meta.db_table, "login_users")
        with self.assertRaises(LookupError):
            apps.get_model("login", "PortalLoginAccount")

    def test_get_renders_login_form(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

    def test_landing_page_has_one_in_page_login_modal(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count(b"data-login-open"), 1)
        self.assertContains(response, '<dialog class="auth-dialog"', html=False)

    def test_username_login_uses_existing_table_and_keeps_plaintext_password(self):
        user = self.create_user("correct-password")
        response = self.post_login(user.user_name, "correct-password")

        self.assertRedirects(response, "/home")
        self.assertEqual(self.client.session["login_id"], str(user.login_id))
        user.refresh_from_db()
        self.assertEqual(user.password, "correct-password")
        self.assertEqual(get_user_for_login(user.user_name).pk, user.pk)
        self.assertEqual(get_api_user_for_login(user.user_name).pk, user.pk)

    def test_login_accepts_legacy_argon2_password_without_changing_table_schema(self):
        password = "legacy-argon-password"
        user = self.create_user(get_hash(password, LEGACY_PASSWORD_SALT))
        response = self.post_login(user.user_name, password)

        self.assertRedirects(response, "/home")
        user.refresh_from_db()
        self.assertEqual(user.password, get_hash(password, LEGACY_PASSWORD_SALT))
        self.assertEqual(users._meta.db_table, "login_users")

    def test_invalid_password_does_not_create_session(self):
        user = self.create_user("correct-password")
        response = self.post_login(user.user_name, "wrong-password")
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("login_id", self.client.session)

    def test_inactive_user_cannot_log_in(self):
        user = self.create_user("correct-password", login_active=False)
        response = self.post_login(user.user_name, "correct-password")
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("login_id", self.client.session)

    def test_home_requires_login_and_logout_clears_session(self):
        self.assertRedirects(self.client.get("/home"), "/login", fetch_redirect_response=False)
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        self.assertEqual(self.client.get("/home").status_code, 200)
        self.client.post("/logout")
        self.assertNotIn("login_id", self.client.session)
        self.assertRedirects(self.client.get("/home"), "/login", fetch_redirect_response=False)

    def test_dashboard_forms_share_application_state_and_product_fields(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        response = self.client.get("/home")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count(b'name="application_number"'), 4)
        self.assertEqual(response.content.count(b'name="state"'), 4)
        self.assertEqual(response.content.count(b'name="product"'), 4)
        self.assertContains(response, "Andhra Pradesh")
        self.assertContains(response, "Dadra and Nagar Haveli and Daman and Diu")
        self.assertContains(response, "Construction Equipment (CE)")

    def test_service_history_is_scoped_to_signed_in_login_users_row(self):
        user = self.create_user()
        service_result.objects.create(login_id=user.login_id, Application_number="OWN-RECORD")
        service_result.objects.create(login_id=user.login_id + 1, Application_number="OTHER-RECORD")
        self.post_login(user.user_name, "plain-password")

        response = self.client.post("/serviceResult", {"login_id": user.login_id + 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["Application_number"] for row in response.json()], ["OWN-RECORD"])

    def test_login_rejects_incorrect_captcha_and_rotates_challenge(self):
        user = self.create_user()
        self.client.get("/login")
        first_answer = self.client.session["login_captcha_answer"]
        response = self.client.post(
            "/login",
            {
                "loginid": user.user_name,
                "psw": "plain-password",
                "captcha_answer": str(int(first_answer) + 1),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("login_id", self.client.session)
        self.assertNotEqual(self.client.session["login_captcha_answer"], first_answer)

    def test_modal_login_returns_dashboard_url(self):
        user = self.create_user()
        self.client.get("/login")
        response = self.client.post(
            "/login",
            {
                "loginid": user.user_name,
                "psw": "plain-password",
                "captcha_answer": self.client.session["login_captcha_answer"],
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "redirect_url": "/home"})

    @override_settings(DEBUG=True)
    def test_demo_command_stores_plaintext_user_in_login_users(self):
        call_command("seed_demo_portal_account", stdout=StringIO())
        user = users.objects.get(user_name="demo")
        self.assertEqual(user.password, "IntellicaDemo!2026")
        self.assertEqual(users._meta.db_table, "login_users")

    @override_settings(DEBUG=True)
    def test_demo_user_can_log_in(self):
        call_command("seed_demo_portal_account", stdout=StringIO())
        response = self.post_login("demo", "IntellicaDemo!2026")
        self.assertRedirects(response, "/home")
        self.assertIn("login_id", self.client.session)

    def test_face_comparison_requires_live_image_and_document_photo(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        response = self.client.post(
            "/cface",
            data=json.dumps({"PAN_INPUT": "aW1hZ2U="}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("live image", response.json()["response_message"])

    def test_face_comparison_calls_existing_service_and_returns_pair_results(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        service_result_data = [{
            "SRC_TITLE": "PAN",
            "TRGT_TITLE": "LIVE",
            "PERCENT": 98.5,
            "FLAG": "MATCH",
        }]
        with (
            patch("Api.idr.upload_Image_to_s3", side_effect=["pan-reference", "live-reference"]),
            patch("Api.idr.getCompareFaces", return_value=({"NUM_IMG": 2, "MATCH": 1, "NO_MATCH": 0}, service_result_data)),
            patch("Api.idr.upload_JSON_to_s3"),
            patch("Api.idr.apiTransaction.transactionCreated"),
            patch("Api.idr.TransactionLog.createServiceResult"),
        ):
            response = self.client.post(
                "/cface",
                data=json.dumps({"PAN_INPUT": image_data, "LIVE_INPUT": image_data}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["result"]["cf_result"], service_result_data)
        self.assertEqual(response.json()["imageid"]["PAN_INPUT"], "pan-reference")

    def test_face_comparison_accepts_multiple_images_and_document_types(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        service_result_data = [
            {"SRC_TITLE": "PAN", "TRGT_TITLE": "LIVE", "PERCENT": 98.5, "FLAG": "MATCH"},
            {"SRC_TITLE": "PAN_2", "TRGT_TITLE": "LIVE", "PERCENT": 87.25, "FLAG": "MATCH"},
            {"SRC_TITLE": "VOTER", "TRGT_TITLE": "LIVE", "PERCENT": 66.1, "FLAG": "MATCH"},
        ]
        with (
            patch("Api.idr.upload_Image_to_s3", side_effect=["pan-1", "pan-2", "voter", "live"]),
            patch("Api.idr.getCompareFaces", return_value=({"NUM_IMG": 4, "MATCH": 3, "NO_MATCH": 0}, service_result_data)) as compare_faces,
            patch("Api.idr.upload_JSON_to_s3"),
            patch("Api.idr.apiTransaction.transactionCreated"),
            patch("Api.idr.TransactionLog.createServiceResult"),
        ):
            response = self.client.post(
                "/cface",
                data=json.dumps({
                    "PAN_INPUT": [image_data, image_data],
                    "VOTER_INPUT": [image_data],
                    "LIVE_INPUT": image_data,
                }),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["imageid"]["PAN_INPUT_2"], "pan-2")
        self.assertEqual(response.json()["result"]["cf_result"], service_result_data)
        compared_images = compare_faces.call_args.args[0]
        self.assertEqual(
            set(compared_images) - {"userId"},
            {"PAN_INPUT", "PAN_INPUT_2", "VOTER_INPUT", "LIVE_INPUT"},
        )

    def test_face_comparison_accepts_numbered_document_image_fields(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        with (
            patch("Api.idr.upload_Image_to_s3", side_effect=["pan-1", "pan-2", "live"]),
            patch("Api.idr.getCompareFaces", return_value=({"NUM_IMG": 3, "MATCH": 0, "NO_MATCH": 3}, [])),
            patch("Api.idr.upload_JSON_to_s3"),
            patch("Api.idr.apiTransaction.transactionCreated"),
            patch("Api.idr.TransactionLog.createServiceResult"),
        ):
            response = self.client.post(
                "/cface",
                data=json.dumps({
                    "PAN_INPUT_1": image_data,
                    "PAN_INPUT_2": image_data,
                    "LIVE_INPUT": image_data,
                }),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["imageid"]["PAN_INPUT_2"], "pan-2")

    def test_face_comparison_persists_selected_report_metadata(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        with (
            patch("Api.idr.upload_Image_to_s3", side_effect=["pan-ref", "live-ref"]),
            patch("Api.idr.getCompareFaces", return_value=({"NUM_IMG": 2, "MATCH": 1, "NO_MATCH": 0}, [])) as compare_faces,
            patch("Api.idr.upload_JSON_to_s3"),
            patch("Api.idr.apiTransaction.transactionCreated"),
            patch("Api.idr.TransactionLog.createServiceResult") as service_result_log,
        ):
            response = self.client.post(
                "/cface",
                data=json.dumps({
                    "PAN_INPUT": image_data,
                    "LIVE_INPUT": image_data,
                    "application_number": "APP-2026-008",
                    "state": "Sikkim",
                    "product": "Construction Equipment (CE)",
                }),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["report_metadata"], {
            "application_number": "APP-2026-008",
            "state": "Sikkim",
            "product": "Construction Equipment (CE)",
        })
        self.assertEqual(compare_faces.call_args.kwargs["request_context"]["product"], "Construction Equipment (CE)")
        self.assertEqual(service_result_log.call_args.kwargs["application_no"], "APP-2026-008")
        self.assertEqual(service_result_log.call_args.kwargs["state"], "Sikkim")

    def test_face_report_download_is_pdf_and_scoped_to_signed_in_user(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        request_id = "face-report-owner-test"
        service_result.objects.create(
            login_id=user.login_id,
            request_id=request_id,
            service_name="Cface",
            Application_number="APP-2026-008",
            State="Sikkim",
        )
        transactions_log.objects.create(
            login_id=user.login_id,
            trx_id=request_id,
            appl_no="APP-2026-008",
            product="Construction Equipment (CE)",
            state="Sikkim",
        )
        service_result.objects.create(
            login_id=user.login_id + 1,
            request_id="face-report-other-user",
            service_name="Cface",
        )
        stored_result = {
            "imageid": {"PAN_INPUT": "pan-ref", "LIVE_INPUT": "live-ref"},
            "result": {
                "cf_overview": {"NUM_IMG": 2, "MATCH": 1, "NO_MATCH": 0, "INVALID": 0},
                "cf_result": [{
                    "SRC_TITLE": "PAN",
                    "TRGT_TITLE": "LIVE",
                    "PERCENT": 98.5,
                    "FLAG": "MATCH",
                }],
            },
        }
        with (
            patch("Services.pdfReport.download_json_from_S3", side_effect=[
                (True, stored_result),
                (True, {"img": image_data}),
                (True, {"img": image_data}),
            ]),
            patch("Services.pdfReport.HTML") as pdf_renderer,
        ):
            pdf_renderer.return_value.write_pdf.return_value = b"%PDF-test"
            response = self.client.get(f"/pdfReport/?trxid={request_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        rendered_html = pdf_renderer.call_args.kwargs["string"]
        self.assertIn("98.5%", rendered_html)
        self.assertIn("data:image/png;base64,", rendered_html)
        self.assertIn("APP-2026-008", rendered_html)
        self.assertIn("Sikkim", rendered_html)
        self.assertIn("Construction Equipment (CE)", rendered_html)
        self.assertIn('class="cover"', rendered_html)
        self.assertIn('class="service-report"', rendered_html)

        unauthorized = self.client.get("/pdfReport/?trxid=face-report-other-user")
        self.assertEqual(unauthorized.status_code, 404)

    def test_face_report_download_finds_legacy_key_without_history_row(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        request_id = "face-report-legacy-key"
        stored_result = {
            "login_id": user.login_id,
            "imageid": {},
            "result": {
                "cf_overview": {"NUM_IMG": 0, "MATCH": 0, "NO_MATCH": 0, "INVALID": 0},
                "cf_result": [],
            },
        }
        with (
            patch("Services.pdfReport.download_json_from_S3", side_effect=[
                (False, 404),
                (True, stored_result),
            ]) as download_result,
            patch("Services.pdfReport.HTML") as pdf_renderer,
        ):
            pdf_renderer.return_value.write_pdf.return_value = b"%PDF-legacy"
            response = self.client.get(f"/pdfReport/?trxid={request_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(download_result.call_args_list[0].args[0], f"intellica-datastorenew/{request_id}.json")
        self.assertEqual(download_result.call_args_list[1].args[0], f"intellica-datastore/{request_id}.json")

    def test_face_report_storage_failure_is_not_reported_as_not_found(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        request_id = "face-report-storage-error"
        with patch(
            "Services.pdfReport.download_json_from_S3",
            return_value=(False, 500),
        ):
            response = self.client.get(f"/pdfReport/?trxid={request_id}")

        self.assertEqual(response.status_code, 503)
        self.assertIn("storage", response.json()["response_message"].lower())

    def test_face_report_post_uses_displayed_result_and_images_without_s3(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        request_id = "face-report-from-visible-result"
        service_result.objects.create(
            login_id=user.login_id,
            request_id=request_id,
            service_name="Cface",
        )
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        displayed_result = {
            "cf_overview": {"NUM_IMG": 2, "MATCH": 1, "NO_MATCH": 0, "INVALID": 0},
            "cf_result": [{
                "SRC_TITLE": "PAN",
                "TRGT_TITLE": "LIVE",
                "PERCENT": 98.5,
                "FLAG": "MATCH",
            }],
        }
        with (
            patch("Services.pdfReport.download_json_from_S3", side_effect=AssertionError("S3 should not be read")),
            patch("Services.pdfReport.HTML") as pdf_renderer,
        ):
            pdf_renderer.return_value.write_pdf.return_value = b"%PDF-visible-result"
            response = self.client.post(
                "/pdfReport/",
                data=json.dumps({
                    "transaction_id": request_id,
                    "result": displayed_result,
                    "images": {"PAN_INPUT": [image_data], "LIVE_INPUT": image_data},
                }),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        rendered_html = pdf_renderer.call_args.kwargs["string"]
        self.assertIn("98.5%", rendered_html)
        self.assertGreaterEqual(rendered_html.count("data:image/png;base64,"), 3)
        self.assertIn("Intellica Technologies Verification Report", rendered_html)
        self.assertIn("Verifier Details", rendered_html)
        self.assertIn(str(user.login_id), rendered_html)

    def test_face_report_post_rejects_transaction_owned_by_another_user(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        service_result.objects.create(
            login_id=user.login_id + 1,
            request_id="other-users-face-report",
            service_name="Cface",
        )
        image_data = base64.b64encode(b"\x89PNG\r\n\x1a\nmock-image").decode("ascii")
        response = self.client.post(
            "/pdfReport/",
            data=json.dumps({
                "transaction_id": "other-users-face-report",
                "result": {"cf_result": []},
                "images": {"PAN_INPUT": image_data, "LIVE_INPUT": image_data},
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_face_comparison_rejects_non_image_base64(self):
        user = self.create_user()
        self.post_login(user.user_name, "plain-password")
        response = self.client.post(
            "/cface",
            data=json.dumps({"PAN_INPUT": "bm90LWltYWdl", "LIVE_INPUT": "bm90LWltYWdl"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("PNG or JPEG", response.json()["response_message"])
