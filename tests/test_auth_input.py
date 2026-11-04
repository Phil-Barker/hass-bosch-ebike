"""Test extracting the authorization code from pasted setup input."""
import pytest

from custom_components.bosch_ebike.api import (
    BoschEBikeAPI,
    BoschEBikeAuthorizationError,
)

REDIRECT = "onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect"


@pytest.mark.parametrize(
    "user_input",
    [
        "abc.123-XYZ",
        "  abc.123-XYZ \n",
        f"{REDIRECT}?code=abc.123-XYZ",
        f"{REDIRECT}?state=s1&session_state=s2&code=abc.123-XYZ&iss=https%3A%2F%2Fp9.authz.bosch.com",
        "code=abc.123-XYZ&state=s1",
        # Windows "Copy as cURL (cmd)" escaping
        f"{REDIRECT}?state=s1^&code=abc.123-XYZ^&iss=https^%^3A^%^2F^%^2Fp9.authz.bosch.com",
    ],
)
def test_extract_authorization_code(user_input):
    """Test that the code is found in all supported input formats."""
    assert BoschEBikeAPI.extract_authorization_code(user_input) == "abc.123-XYZ"


def test_extract_authorization_code_bosch_error():
    """Test that an error redirect from Bosch is reported, not used as a code (#24)."""
    user_input = (
        "http://com.bosch.ebike.onebikeapp/oauth2redirect?error=temporarily_unavailable"
        "^&error_description=authentication_expired^&state=a8Z5KZvl0D5dTEF6qlBMsc0oAtLzWJHLjcZe_6KSS-U"
        "^&iss=https^%^3A^%^2F^%^2Fp9.authz.bosch.com^%^2Fauth^%^2Frealms^%^2Fobc^"
    )

    with pytest.raises(BoschEBikeAuthorizationError) as err:
        BoschEBikeAPI.extract_authorization_code(user_input)

    assert err.value.reason == "authorization_rejected"
    assert "authentication_expired" in str(err.value)


@pytest.mark.parametrize("user_input", ["", "   ", f"{REDIRECT}?code=", f"{REDIRECT}?code=&state=s1"])
def test_extract_authorization_code_missing(user_input):
    """Test that empty input or a URL without a code is reported."""
    with pytest.raises(BoschEBikeAuthorizationError) as err:
        BoschEBikeAPI.extract_authorization_code(user_input)

    assert err.value.reason == "missing_code"
