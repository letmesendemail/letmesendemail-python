from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://letmesend.email/api/v1"
DEFAULT_TIMEOUT_MS = 30_000
DEFAULT_RETRIES = 0


@dataclass
class ClientConfig:
    api_key: str
    base_url: str = field(default=DEFAULT_BASE_URL)
    timeout_ms: int = field(default=DEFAULT_TIMEOUT_MS)
    retries: int = field(default=DEFAULT_RETRIES)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
