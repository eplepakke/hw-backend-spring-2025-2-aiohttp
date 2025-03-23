import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await super().connect(app)
        await self.create_admin(
            email=app.config.admin.email, password=app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(id=len(self.app.database.admins) + 1,
                      email=email,
                      password=sha256(password.encode()).hexdigest()
                      )
        self.app.database.admins.append(admin)
        return admin