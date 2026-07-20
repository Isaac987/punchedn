from enum import StrEnum


class UserPermissions(StrEnum):
    READ = "users:read"
    WRITE = "users:write"
