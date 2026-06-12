from marshmallow import Schema, fields, validate


class UpdateMembershipSchema(Schema):
    """
    관리자 회원 등급 변경 요청 검증.
    """

    membership_type = fields.String(
        required=True,
        validate=validate.OneOf(["free", "premium", "admin"]),
        error_messages={"required": "회원 등급은 필수입니다."}
    )


class UpdateActiveSchema(Schema):
    """
    관리자 회원 활성화 상태 변경 요청 검증.
    """

    is_active = fields.Boolean(
        required=True,
        error_messages={"required": "활성화 상태는 필수입니다."}
    )