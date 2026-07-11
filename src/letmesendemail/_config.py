"""SDK client configuration."""

from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://letmesend.email/api/v1"
DEFAULT_TIMEOUT_MS = 30_000
DEFAULT_RETRIES = 0
MAX_RETRY_DELAY = 300


@dataclass
class ClientConfig:
    """Configuration for the LetMeSendEmail client."""

    api_key: str
    base_url: str = field(default=DEFAULT_BASE_URL)
    timeout_ms: int = field(default=DEFAULT_TIMEOUT_MS)
    retries: int = field(default=DEFAULT_RETRIES)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if not isinstance(self.timeout_ms, int) or self.timeout_ms <= 0:
            self.timeout_ms = DEFAULT_TIMEOUT_MS
        if not isinstance(self.retries, int) or self.retries < 0:
            self.retries = DEFAULT_RETRIES
