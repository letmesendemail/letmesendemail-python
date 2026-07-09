from letmesendemail._errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    _error_from_response,
)


class TestErrors:
    def test_all_error_classes(self):
        assert issubclass(ApiError, Exception)
        assert issubclass(AuthenticationError, Exception)
        assert issubclass(AuthorizationError, Exception)
        assert issubclass(ValidationError, Exception)
        assert issubclass(RateLimitError, Exception)
        assert issubclass(NotFoundError, Exception)
        assert issubclass(ConflictError, Exception)
        assert issubclass(NetworkError, Exception)
        assert issubclass(TimeoutError, Exception)

    def test_401_maps_to_authentication_error(self):
        err = _error_from_response(401, {"message": "Unauthorized", "name": "unauthorized"}, {})
        assert isinstance(err, AuthenticationError)
        assert err.message == "Unauthorized"
        assert err.api_code == "unauthorized"

    def test_404_maps_to_not_found_error(self):
        err = _error_from_response(404, {"message": "Not found"}, {})
        assert isinstance(err, NotFoundError)

    def test_422_maps_to_validation_error(self):
        body = {"message": "Invalid", "errors": {"email": ["Required"]}}
        err = _error_from_response(422, body, {})
        assert isinstance(err, ValidationError)
        assert err.validation_errors == {"email": ["Required"]}

    def test_429_maps_to_rate_limit_error(self):
        err = _error_from_response(429, {"message": "Limited"}, {"retry-after": "120"})
        assert isinstance(err, RateLimitError)
        assert err.retry_after == 120

    def test_500_maps_to_api_error(self):
        err = _error_from_response(500, {"message": "Server error"}, {})
        assert isinstance(err, ApiError)

    def test_400_maps_to_validation_error(self):
        err = _error_from_response(400, {"message": "Bad request"}, {})
        assert isinstance(err, ValidationError)

    def test_403_maps_to_authorization_error(self):
        err = _error_from_response(403, {"message": "Forbidden"}, {})
        assert isinstance(err, AuthorizationError)

    def test_409_maps_to_conflict_error(self):
        err = _error_from_response(409, {"message": "Conflict"}, {})
        assert isinstance(err, ConflictError)

    def test_413_maps_to_validation_error(self):
        err = _error_from_response(413, {"message": "Too large"}, {})
        assert isinstance(err, ValidationError)
