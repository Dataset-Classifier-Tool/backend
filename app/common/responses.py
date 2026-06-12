from flask import jsonify


def success_response(data=None, message="success", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code


def error_response(message="error", status_code=400, details=None):
    return jsonify({
        "success": False,
        "message": message,
        "details": details
    }), status_code