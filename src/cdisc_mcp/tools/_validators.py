"""Input validators for MCP tool parameters."""


def validate_version(version: str, param_name: str = "version") -> str:
    """Validate and return a safe version string.

    Args:
        version: Version string to validate.
        param_name: Parameter name for error messages.

    Returns:
        Stripped version string.

    Raises:
        ValueError: If version contains path traversal characters.
    """
    version = version.strip()
    if not version:
        raise ValueError(f"{param_name} must not be empty")
    if "/" in version or ".." in version:
        raise ValueError(
            f"{param_name} '{version}' contains invalid characters"
        )
    return version
