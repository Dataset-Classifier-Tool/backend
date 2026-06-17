"""
exceptions.py

공통 커스텀 예외 정의 파일.
Service 계층에서 발생한 예외를 Route 계층에서 일관되게 처리하기 위해 사용한다.
"""


class AppError(Exception):
    """
    애플리케이션 공통 예외.
    """

    def __init__(self, message: str, status_code: int = 400, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ValidationAppError(AppError):
    """
    요청 데이터 검증 실패 예외.
    """

    def __init__(self, message: str, details=None):
        super().__init__(message, status_code=400, details=details)


class NotFoundAppError(AppError):
    """
    리소스를 찾을 수 없을 때 사용하는 예외.
    """

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class UnauthorizedAppError(AppError):
    """
    인증 실패 예외.
    """

    def __init__(self, message: str = "인증이 필요합니다."):
        super().__init__(message, status_code=401)


class ForbiddenAppError(AppError):
    """
    권한 부족 예외.
    """

    def __init__(self, message: str = "접근 권한이 없습니다."):
        super().__init__(message, status_code=403)