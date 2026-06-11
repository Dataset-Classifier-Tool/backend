"""
auth_schema.py

인증 관련 요청 데이터 검증 스키마.

역할:
- 회원가입 요청 데이터 검증
- 로그인 요청 데이터 검증

예:
회원가입 요청
{
    "email": "test@test.com",
    "password": "12345678",
    "nickname": "도균"
}
"""

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """
    회원가입 요청 데이터 검증용 Schema.
    """

    email = fields.Email(
        required=True,
        error_messages={
            "required": "이메일은 필수입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        }
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "비밀번호는 필수입니다.",
        }
    )

    nickname = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={
            "required": "닉네임은 필수입니다.",
        }
    )


class LoginSchema(Schema):
    """
    로그인 요청 데이터 검증용 Schema.
    """

    email = fields.Email(
        required=True,
        error_messages={
            "required": "이메일은 필수입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        }
    )

    password = fields.String(
        required=True,
        error_messages={
            "required": "비밀번호는 필수입니다.",
        }
    )