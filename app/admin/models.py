from dataclasses import dataclass
from hashlib import sha256
from typing import Optional


@dataclass
class Admin:
    id: int
    email: str
    password: str | None = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: dict | None) -> Optional['Admin']:
        return cls(id=session['admin']['id'], email=session['admin']['email'])
