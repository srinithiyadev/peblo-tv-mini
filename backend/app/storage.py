from abc import ABC, abstractmethod
from pathlib import Path
import shutil


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Persist bytes under key, return a path/URL to read them back."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        ...

    @abstractmethod
    def url(self, key: str) -> str:
        """Public-ish reference the catalogue/CMS can use."""


class LocalStorage(Storage):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def read(self, key: str) -> bytes:
        return (self.root / key).read_bytes()

    def url(self, key: str) -> str:
        # In prod this becomes the R2 public URL builder.
        return f"/static/{key}"


def get_storage() -> Storage:
    return LocalStorage(Path(__file__).resolve().parents[1] / "uploads")