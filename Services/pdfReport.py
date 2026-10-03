
from base64                                import b64decode, b64encode
from io                                    import BytesIO
from django.conf                            import settings
from django.http                            import HttpResponse, JsonResponse
from django.shortcuts                       import redirect
from django.template.loader                 import render_to_string
from django.utils import timezone
from json                                   import JSONDecodeError, loads as load_json
from login.views                            import require_login
from Services.AWS                           import download_json_from_S3
from Services.models                        import service_result, transactions_log

try:
    from weasyprint import HTML
except Exception as ex:
    HTML = None
    print(f"Error, Pdf reports are not available! Reason being {ex}")


def get_result_with_images(stored_result):
    """Replace stored S3 image references with base64 content for PDF rendering."""
    image_data = stored_result.get("imageid", {})
    for image_name, image_path in list(image_data.items()):
        downloaded = download_json_from_S3(image_path)
        if downloaded[0] and isinstance(downloaded[1], dict):
            image_data[image_name] = downloaded[1].get("img", "")
    return stored_result


def image_data_uri_for_title(image_data, title):
    for image_name, image_value in image_data.items():
        if image_name.replace("_INPUT", "") == title:
            try:
                image_bytes = b64decode(image_value, validate=True)
            except (TypeError, ValueError):
                return ""
            try:
                from PIL import Image

                with Image.open(BytesIO(image_bytes)) as source_image:
                    source_image.thumbnail((360, 360))
                    preview = source_image.convert("RGB")
                    preview_data = BytesIO()
                    preview.save(preview_data, format="JPEG", quality=72, optimize=True)
                return f"data:image/jpeg;base64,{b64encode(preview_data.getvalue()).decode('ascii')}"
            except Exception:
                pass
            mime_type = "image/jpeg" if image_bytes.startswith(b"\xff\xd8\xff") else "image/png"
            return f"data:{mime_type};base64,{image_value}"
    return ""


def normalize_report_images(images):
    """Validate and flatten document image arrays into the compare-service keys."""
    allowed_types = ("PAN_INPUT", "AADHAAR_INPUT", "VOTER_INPUT", "DL_INPUT", "PASSPORT_INPUT")
    normalized = {}
    if not isinstance(images, dict):
        raise ValueError("Image data must be an object.")

    for field_name, field_value in images.items():
        image_type = next(
            (
                name for name in (*allowed_types, "LIVE_INPUT")
                if field_name == name
                or (
                    name != "LIVE_INPUT"
                    and field_name.startswith(f"{name}_")
                    and field_name[len(name) + 1 :].isdigit()
                )
            ),
            None,
        )
        if image_type is None:
            raise ValueError(f"Unsupported image type: {field_name}.")
        values = field_value if isinstance(field_value, list) else [field_value]
        if not values:
            raise ValueError(f"{field_name} must include at least one image.")
        if image_type == "LIVE_INPUT" and len(values) != 1:
            raise ValueError("Exactly one live image is required.")

        is_numbered = field_name != image_type
        for index, value in enumerate(values, start=1):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must contain valid image data.")
            if len(value) > 7_000_000:
                raise ValueError(f"{field_name} exceeds the 5 MB upload limit.")
            try:
                decoded = b64decode(value, validate=True)
            except (TypeError, ValueError) as ex:
                raise ValueError(f"{field_name} is not valid base64 image data.") from ex
            if not decoded.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")):
                raise ValueError(f"{field_name} must be a PNG or JPEG image.")

            if is_numbered:
                image_name = field_name if len(values) == 1 else f"{field_name}_{index}"
            else:
                image_name = image_type if index == 1 else f"{image_type}_{index}"
            if image_name in normalized:
                raise ValueError(f"Duplicate image field: {image_name}.")
            normalized[image_name] = value

    if len(normalized) > 10:
        raise ValueError("A maximum of 10 images, including the live image, can be included.")
    if "LIVE_INPUT" not in normalized or not any(name != "LIVE_INPUT" for name in normalized):
        raise ValueError("A live image and at least one document image are required.")
    return normalized


def create_face_pdf_response(transaction_id, comparison_result, image_data, verifier_details=None):
    if not isinstance(comparison_result, dict):
        raise ValueError("Comparison result is missing or invalid.")
    result_pairs = comparison_result.get("cf_result")
    if not isinstance(result_pairs, list):
        raise ValueError("Image-pair results are missing or invalid.")

    images = [
        {
            "title": image_name.replace("_INPUT", ""),
            "image_uri": image_data_uri_for_title(image_data, image_name.replace("_INPUT", "")),
        }
        for image_name in image_data
    ]
    image_uris_by_title = {image["title"]: image["image_uri"] for image in images}
    pairs = []
    for pair in result_pairs:
        if not isinstance(pair, dict):
            raise ValueError("An image-pair result is invalid.")
        pair_data = dict(pair)
        match_flag = str(pair_data.get("FLAG", "")).strip().upper()
        pair_data["IS_MATCH"] = match_flag in {"MATCH", "SAME_IMAGE"}
        pair_data["DISPLAY_FLAG"] = "Match" if pair_data["IS_MATCH"] else (
            "No Match" if match_flag in {"NOMATCH", "NO_MATCH"} else pair_data.get("FLAG", "No result")
        )
        pair_data["SRC_IMAGE_URI"] = image_uris_by_title.get(pair_data.get("SRC_TITLE", ""), "")
        pair_data["TRGT_IMAGE_URI"] = image_uris_by_title.get(pair_data.get("TRGT_TITLE", ""), "")
        pairs.append(pair_data)

    logo_path = settings.BASE_DIR / "Landing" / "static" / "img" / "logo.png"
    try:
        logo_uri = f"data:image/png;base64,{b64encode(logo_path.read_bytes()).decode('ascii')}"
    except OSError:
        logo_uri = ""

    html = render_to_string(
        "cface_pdf_report.html",
        {
            "transaction_id": transaction_id,
            "images": images,
            "pairs": pairs,
            "overview": comparison_result.get("cf_overview", {}),
            "verifier": verifier_details or {},
            "logo_uri": logo_uri,
            "generated_at": timezone.localtime().strftime("%d %b %Y, %I:%M %p"),
        },
    )
    pdf_content = HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Cface_Result_{transaction_id}.pdf"'
    return response


def get_report_verifier_details(user, transaction_id, saved_metadata=None):
    saved_metadata = saved_metadata if isinstance(saved_metadata, dict) else {}
    service_record = service_result.objects.filter(
        request_id=transaction_id,
        login_id=user.login_id,
    ).first()
    transaction_record = transactions_log.objects.filter(
        trx_id=transaction_id,
        login_id=user.login_id,
    ).order_by("sno").first()

    def first_report_value(*values):
        return next(
            (str(value).strip() for value in values if value is not None and str(value).strip() and str(value).strip() != "Test"),
            "",
        )

    application_number = first_report_value(
        saved_metadata.get("application_number"),
        getattr(service_record, "Application_number", ""),
        getattr(transaction_record, "appl_no", ""),
    ) or transaction_id
    state = first_report_value(
        saved_metadata.get("state"),
        getattr(service_record, "State", ""),
        getattr(transaction_record, "state", ""),
    ) or user.state
    product = first_report_value(
        saved_metadata.get("product"),
        getattr(transaction_record, "product", ""),
    ) or "Face Comparison"

    return {
        "login_id": user.login_id,
        "user_name": user.user_name,
        "application_number": application_number,
        "state": state,
        "product": product,
    }


def cface_report(request):
    user = require_login(request)
    if not user:
        if request.method == "POST":
            return JsonResponse(
                {"success": False, "response_message": "Please sign in again to download this report."},
                status=401,
            )
        return redirect("/login")

    if request.method == "POST":
        if HTML is None:
            return JsonResponse(
                {"success": False, "response_message": "PDF report generation is unavailable."},
                status=503,
            )
        try:
            payload = load_json(request.body.decode("utf-8"))
            transaction_id = payload.get("transaction_id") if isinstance(payload, dict) else None
            if not isinstance(transaction_id, str) or not transaction_id or len(transaction_id) > 64:
                raise ValueError("A valid comparison transaction ID is required.")

            owns_transaction = service_result.objects.filter(
                request_id=transaction_id,
                login_id=user.login_id,
            ).exists() or transactions_log.objects.filter(
                trx_id=transaction_id,
                login_id=user.login_id,
            ).exists()
            if not owns_transaction:
                return JsonResponse(
                    {"success": False, "response_message": "This comparison is not available for your account."},
                    status=404,
                )

            image_data = normalize_report_images(payload.get("images"))
            verifier_details = get_report_verifier_details(
                user,
                transaction_id,
                payload.get("report_metadata"),
            )
            response = create_face_pdf_response(
                transaction_id,
                payload.get("result"),
                image_data,
                verifier_details,
            )
            return response
        except (JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError, ValueError) as ex:
            return JsonResponse({"success": False, "response_message": str(ex)}, status=400)
        except Exception as ex:
            print(f"Unable to generate face-comparison PDF: {ex}")
            return JsonResponse(
                {"success": False, "response_message": "The PDF report could not be generated."},
                status=503,
            )

    request_id = request.GET.get('trxid')
    if not request_id:
        return JsonResponse(
            {"success": False, "response_message": "The requested face-comparison report was not found."},
            status=404,
        )

    if HTML is None:
        return JsonResponse(
            {"success": False, "response_message": "PDF report generation is unavailable."},
            status=503,
        )

    has_any_service_result = service_result.objects.filter(request_id=request_id).exists()
    has_owned_service_result = service_result.objects.filter(
        request_id=request_id,
        login_id=user.login_id,
    ).exists()
    has_any_transaction_log = transactions_log.objects.filter(trx_id=request_id).exists()
    has_owned_transaction_log = transactions_log.objects.filter(
        trx_id=request_id,
        login_id=user.login_id,
    ).exists()
    has_transaction_record = has_any_service_result or has_any_transaction_log
    has_owned_transaction_record = has_owned_service_result or has_owned_transaction_log
    if has_transaction_record and not has_owned_transaction_record:
        return JsonResponse(
            {"success": False, "response_message": "The requested face-comparison report was not found."},
            status=404,
        )

    stored_result = (False, None)
    storage_unavailable = False
    for result_key in (
        f"intellica-datastorenew/{request_id}.json",
        f"intellica-datastore/{request_id}.json",
        f"{request_id}.json",
    ):
        try:
            stored_result = download_json_from_S3(result_key)
        except Exception as ex:
            print(f"Unable to read face report {request_id} from S3: {ex}")
            storage_unavailable = True
            continue
        if stored_result[0] and isinstance(stored_result[1], dict):
            break
        if not stored_result[0] and stored_result[1] != 404:
            storage_unavailable = True

    if not stored_result[0] or not isinstance(stored_result[1], dict):
        if storage_unavailable:
            return JsonResponse(
                {
                    "success": False,
                    "response_message": "The report storage could not be reached. Check S3 access and try again.",
                },
                status=503,
            )
        return JsonResponse(
            {"success": False, "response_message": "The requested face-comparison report was not found."},
            status=404,
        )

    stored_login_id = stored_result[1].get("login_id")
    stored_result_belongs_to_user = (
        stored_login_id is not None and str(stored_login_id) == str(user.login_id)
    )
    if not (has_owned_service_result or has_owned_transaction_log or stored_result_belongs_to_user):
        return JsonResponse(
            {"success": False, "response_message": "The requested face-comparison report was not found."},
            status=404,
        )

    stored_result = get_result_with_images(stored_result[1])
    image_data = stored_result.get("imageid", {})
    comparison_result = stored_result.get("result", {})
    try:
        return create_face_pdf_response(
            request_id,
            comparison_result,
            image_data,
            get_report_verifier_details(user, request_id, stored_result.get("report_metadata")),
        )
    except Exception as ex:
        print(f"Unable to generate face-comparison PDF: {ex}")
        return JsonResponse(
            {"success": False, "response_message": "The PDF report could not be generated."},
            status=503,
        )
