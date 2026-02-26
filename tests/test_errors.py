# -*- coding: utf-8 -*-
"""Unit tests for src/cdisc_mcp/errors.py"""

import pytest


class TestCDISCClientError:
    """CDISCClientError is the base exception for all CDISC client errors."""

    def test_is_exception_subclass(self):
        from cdisc_mcp.errors import CDISCClientError

        assert issubclass(CDISCClientError, Exception)

    def test_can_be_raised_and_caught(self):
        from cdisc_mcp.errors import CDISCClientError

        with pytest.raises(CDISCClientError):
            raise CDISCClientError("test error")

    def test_message_preserved(self):
        from cdisc_mcp.errors import CDISCClientError

        err = CDISCClientError("something went wrong")
        assert "something went wrong" in str(err)


class TestAuthenticationError:
    """AuthenticationError represents a rejected API key (HTTP 401)."""

    def test_is_cdisc_client_error_subclass(self):
        from cdisc_mcp.errors import AuthenticationError, CDISCClientError

        assert issubclass(AuthenticationError, CDISCClientError)

    def test_can_be_raised_and_caught_as_base(self):
        from cdisc_mcp.errors import AuthenticationError, CDISCClientError

        with pytest.raises(CDISCClientError):
            raise AuthenticationError("Invalid API key")

    def test_message_preserved(self):
        from cdisc_mcp.errors import AuthenticationError

        err = AuthenticationError("Invalid CDISC API key (HTTP 401)")
        assert "401" in str(err)


class TestRateLimitError:
    """RateLimitError represents exhausted retries on HTTP 429."""

    def test_is_cdisc_client_error_subclass(self):
        from cdisc_mcp.errors import CDISCClientError, RateLimitError

        assert issubclass(RateLimitError, CDISCClientError)

    def test_default_message_without_retry_after(self):
        from cdisc_mcp.errors import RateLimitError

        err = RateLimitError()
        assert "Rate limit exceeded" in str(err)
        assert err.retry_after is None

    def test_message_includes_retry_after_when_provided(self):
        from cdisc_mcp.errors import RateLimitError

        err = RateLimitError(retry_after=60)
        assert "60" in str(err)
        assert err.retry_after == 60

    def test_retry_after_none_when_not_provided(self):
        from cdisc_mcp.errors import RateLimitError

        err = RateLimitError()
        assert err.retry_after is None


class TestResourceNotFoundError:
    """ResourceNotFoundError represents a missing resource (HTTP 404)."""

    def test_is_cdisc_client_error_subclass(self):
        from cdisc_mcp.errors import CDISCClientError, ResourceNotFoundError

        assert issubclass(ResourceNotFoundError, CDISCClientError)

    def test_can_be_raised_and_caught(self):
        from cdisc_mcp.errors import ResourceNotFoundError

        with pytest.raises(ResourceNotFoundError):
            raise ResourceNotFoundError("Resource not found")
