from django.shortcuts import redirect, render
from Services.models import service_result

from login.views import require_login

# Create your views here.
INDIAN_STATES_AND_UTS = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
)

AVAILABLE_PRODUCTS = (
    "Personal Loan",
    "Home Loan",
    "Two Wheeler Loan",
    "Vehicle Loan",
    "Construction Equipment (CE)",
    "Business Loan",
    "Consumer Durable Loan",
    "Other",
)

def Home(request):
    user = require_login(request)
    if not user:
        return redirect("/login")
    login_id = user.login_id
    client_name = user.client_name
    requests = service_result.objects.filter(login_id=login_id).order_by("-timestamp")
    return render(
        request,
        "home.html",
        {
            "user": user,
            "login_id": login_id,
            "client_name": client_name,
            "recent_requests": requests[:5],
            "all_requests": requests,
            "total_requests": requests.count(),
            "kyc_requests": requests.filter(service_name__icontains="KYC").count(),
            "idr_requests": requests.filter(service_name__icontains="IDR").count(),
            "states": INDIAN_STATES_AND_UTS,
            "products": AVAILABLE_PRODUCTS,
        },
    )