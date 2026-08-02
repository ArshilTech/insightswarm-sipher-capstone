from fastapi_users import schemas
import uuid

# UserRead schema for reading user information
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

# UserCreate schema for user registration
class UserCreate(schemas.BaseUserCreate):
    pass

# UserUpdate schema for updating user information
class UserUpdate(schemas.BaseUserUpdate):
    pass