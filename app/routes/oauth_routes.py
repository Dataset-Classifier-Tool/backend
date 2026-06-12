from urllib.parse import urlencode

from flask import Blueprint, current_app, redirect, request

from app.common.responses import error_response
from app.services.oauth_service import OAuthService

oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/auth/oauth")


@oauth_bp.get("/kakao/login")
def kakao_login():
    login_url = OAuthService.get_kakao_login_url()
    return redirect(login_url)


@oauth_bp.get("/kakao/callback")
def kakao_callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return error_response(f"카카오 로그인 실패: {error}", 400)

    if not code:
        return error_response("카카오 인가 코드가 없습니다.", 400)

    try:
        result = OAuthService.handle_kakao_callback(code)
        return redirect_to_frontend(result)

    except Exception as e:
        return redirect_to_frontend_error(str(e))


@oauth_bp.get("/naver/login")
def naver_login():
    login_url = OAuthService.get_naver_login_url()
    return redirect(login_url)


@oauth_bp.get("/naver/callback")
def naver_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")

    if error:
        return error_response(f"네이버 로그인 실패: {error}", 400)

    if not code:
        return error_response("네이버 인가 코드가 없습니다.", 400)

    try:
        result = OAuthService.handle_naver_callback(code, state)
        return redirect_to_frontend(result)

    except Exception as e:
        return redirect_to_frontend_error(str(e))


def redirect_to_frontend(result: dict):
    frontend_url = current_app.config["OAUTH_FRONTEND_REDIRECT_URL"]

    query = urlencode({
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
    })

    return redirect(f"{frontend_url}?{query}")


def redirect_to_frontend_error(message: str):
    frontend_url = current_app.config["OAUTH_FRONTEND_REDIRECT_URL"]

    query = urlencode({
        "error": message,
    })

    return redirect(f"{frontend_url}?{query}")