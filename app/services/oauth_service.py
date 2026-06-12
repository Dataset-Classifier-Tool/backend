import secrets
from urllib.parse import urlencode

import requests
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


class OAuthService:
    """
    카카오/네이버 OAuth 로그인 서비스.

    역할:
    - 로그인 URL 생성
    - 인가 코드로 access token 요청
    - access token으로 사용자 프로필 조회
    - 기존 회원 조회 또는 신규 회원 생성
    - 우리 서비스 JWT 발급
    """

    @staticmethod
    def get_kakao_login_url() -> str:
        params = {
            "response_type": "code",
            "client_id": current_app.config["KAKAO_CLIENT_ID"],
            "redirect_uri": current_app.config["KAKAO_REDIRECT_URI"],
        }

        return "https://kauth.kakao.com/oauth/authorize?" + urlencode(params)

    @staticmethod
    def get_naver_login_url() -> str:
        state = secrets.token_urlsafe(16)

        params = {
            "response_type": "code",
            "client_id": current_app.config["NAVER_CLIENT_ID"],
            "redirect_uri": current_app.config["NAVER_REDIRECT_URI"],
            "state": state,
        }

        return "https://nid.naver.com/oauth2.0/authorize?" + urlencode(params)

    @staticmethod
    def handle_kakao_callback(code: str) -> dict:
        token_response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": current_app.config["KAKAO_CLIENT_ID"],
                "redirect_uri": current_app.config["KAKAO_REDIRECT_URI"],
                "code": code,
                "client_secret": current_app.config.get("KAKAO_CLIENT_SECRET") or "",
            },
            timeout=10,
        )

        if token_response.status_code != 200:
            raise ValueError(f"카카오 토큰 발급 실패: {token_response.text}")

        access_token = token_response.json().get("access_token")

        profile_response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )

        if profile_response.status_code != 200:
            raise ValueError(f"카카오 프로필 조회 실패: {profile_response.text}")

        profile = profile_response.json()

        kakao_id = str(profile.get("id"))
        kakao_account = profile.get("kakao_account", {})
        properties = profile.get("properties", {})

        email = kakao_account.get("email") or f"kakao_{kakao_id}@oauth.local"
        nickname = properties.get("nickname") or f"kakao_{kakao_id}"
        name = kakao_account.get("name") or nickname
        birth_date = None

        user = OAuthService.get_or_create_oauth_user(
            provider="kakao",
            provider_id=kakao_id,
            email=email,
            nickname=nickname,
            name=name,
            birth_date=birth_date,
        )

        return OAuthService.create_login_result(user)

    @staticmethod
    def handle_naver_callback(code: str, state: str | None) -> dict:
        token_response = requests.get(
            "https://nid.naver.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": current_app.config["NAVER_CLIENT_ID"],
                "client_secret": current_app.config["NAVER_CLIENT_SECRET"],
                "code": code,
                "state": state,
            },
            timeout=10,
        )

        if token_response.status_code != 200:
            raise ValueError(f"네이버 토큰 발급 실패: {token_response.text}")

        access_token = token_response.json().get("access_token")

        profile_response = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )

        if profile_response.status_code != 200:
            raise ValueError(f"네이버 프로필 조회 실패: {profile_response.text}")

        profile = profile_response.json().get("response", {})

        naver_id = str(profile.get("id"))
        email = profile.get("email") or f"naver_{naver_id}@oauth.local"
        nickname = profile.get("nickname") or f"naver_{naver_id}"
        name = profile.get("name") or nickname
        birth_date = None

        user = OAuthService.get_or_create_oauth_user(
            provider="naver",
            provider_id=naver_id,
            email=email,
            nickname=nickname,
            name=name,
            birth_date=birth_date,
        )

        return OAuthService.create_login_result(user)

    @staticmethod
    def get_or_create_oauth_user(
        provider: str,
        provider_id: str,
        email: str,
        nickname: str,
        name: str,
        birth_date,
    ) -> User:
        existing_oauth_user = UserRepository.find_by_provider(
            provider=provider,
            provider_id=provider_id,
        )

        if existing_oauth_user:
            return existing_oauth_user

        existing_email_user = UserRepository.find_by_email(email)

        if existing_email_user:
            raise ValueError(
                "이미 같은 이메일로 가입된 계정이 있습니다. 일반 로그인으로 이용해주세요."
            )

        user = User(
            name=name,
            birth_date=birth_date,
            nickname=nickname,
            email=email,
            password_hash=None,
            membership_type="free",
            provider=provider,
            provider_id=provider_id,
            is_active=True,
        )

        return UserRepository.create(user)

    @staticmethod
    def create_login_result(user: User) -> dict:
        if not user.is_active:
            raise ValueError("비활성화된 계정입니다.")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": AuthService.serialize_user(user),
        }