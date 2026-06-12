from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """
    일반 회원가입 요청 검증.

    요청 예:
    {
        "name": "김도균",
        "birth_date": "1995-01-01",
        "nickname": "도균",
        "email": "test@test.com",
        "password": "12345678"
    }
    """

    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "이름은 필수입니다."}
    )

    birth_date = fields.Date(
        required=True,
        error_messages={
            "required": "생년월일은 필수입니다.",
            "invalid": "생년월일 형식은 YYYY-MM-DD 입니다."
        }
    )

    nickname = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "닉네임은 필수입니다."}
    )

    email = fields.Email(
        required=True,
        error_messages={
            "required": "이메일은 필수입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다."
        }
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        error_messages={"required": "비밀번호는 필수입니다."}
    )


class LoginSchema(Schema):
    """
    일반 로그인 요청 검증.
    """

    email = fields.Email(
        required=True,
        error_messages={
            "required": "이메일은 필수입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다."
        }
    )

    password = fields.String(
        required=True,
        error_messages={"required": "비밀번호는 필수입니다."}
    )