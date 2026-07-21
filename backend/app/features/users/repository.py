from .models import UserModel


class UserRepository:
    # TODO: Implement UserRepository
    async def get_by_auth_id(self, auth_id: str) -> UserModel: ...
