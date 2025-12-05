from flask import jsonify

def error_response(code, message, status_code=400, details=None):
    payload = {
        "error": {
            "code": code,
            "message": message
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status_code


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return error_response("BAD_REQUEST", "Bad request", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response("UNAUTHORIZED", "Missing or invalid bearer token", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error_response("FORBIDDEN", "Forbidden", 403)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("NOT_FOUND", "Resource not found", 404)

    @app.errorhandler(409)
    def conflict(e):
        return error_response("RESOURCE_CONFLICT", "Resource conflict", 409)

    @app.errorhandler(422)
    def unprocessable(e):
        return error_response("UNPROCESSABLE_ENTITY", "Unprocessable entity", 422)

    @app.errorhandler(413)
    def payload_too_large(e):
        return error_response("PAYLOAD_TOO_LARGE", "Payload too large", 413)

    @app.errorhandler(500)
    def internal(e):
        return error_response("INTERNAL_ERROR", "Internal server error", 500)
