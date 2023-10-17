"""File-related errors used by this package's modules."""


class FileContentError(RuntimeError):
    """The file content is invalid."""


class FileExtensionInvalidError(RuntimeError):
    """The file extension is invalid."""
