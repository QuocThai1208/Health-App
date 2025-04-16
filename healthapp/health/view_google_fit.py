from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
import requests


# hàm khởi động quá trình xác thực oauth2 và chuyển hướng sáng trang đăng nhập
def google_fit_login(request):
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_FIT_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_FIT_REDIRECT_URI}"
        f"&scope={settings.GOOGLE_FIT_SCOPE}"
        "&access_type=offline"  # nhận refresh_token
        "&prompt=consent"  # Buộc Google hiển thị màn hình xác nhận quyền
    )
    return redirect(auth_url)


#hàm dùng để xác thực người dùng
def google_fit_callback(request):
    #lấy authorization code sau khi người dùng cấp quyền thông qua tham số code trong url
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)
    #gửi yêu cầu đến token_url để lấy token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_FIT_CLIENT_ID,
        "client_secret": settings.GOOGLE_FIT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI,
    }

    response = requests.post(token_url, data=data)
    tokens = response.json()

    if "access_token" not in tokens:
        return JsonResponse({"error": "Failed to obtain access token", "details": tokens}, status=400)

    access_token = tokens.get("access_token")

    # chuyển hướng
    return redirect(f"/users/current-user/health-data/?access_token={access_token}")