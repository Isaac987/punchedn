from typing import List, Optional

from beanie import PydanticObjectId

from .models import UserModel


# TODO: Implement UserRepository
class UserRepository:
    async def create(self, user: UserModel) -> UserModel:
        await user.create()

        return user

    async def get_by_id(self, id: PydanticObjectId) -> Optional[UserModel]:
        return await UserModel.get(id)

    async def get_by_auth_id(self, auth_id: str) -> Optional[UserModel]:
        return await UserModel.find_one(UserModel.auth_id == auth_id)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        return await UserModel.find_one(UserModel.email == email)

    async def get_all_active_users(self) -> List[UserModel]:
        return await UserModel.find_all(UserModel.is_active)

    async def update_user(self, user: UserModel) -> UserModel:
        return await UserModel.save()
