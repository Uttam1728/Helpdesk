from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    STAFF = 'staff'
    PARENT = 'parent'


class CommonConstants:
    JWT_TOKEN_SWAGGER_DESCRIPTION = 'JWT token in format: Token <access_token>'