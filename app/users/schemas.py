from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator, ConfigDict
from typing import Optional
import re

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def password_complexity(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^\w\s]", password):
            raise ValueError("Password must contain at least one symbol")
        return password

class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class UserUpdate(BaseModel):
    username: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None

    @model_validator(mode='before')
    def check_passwords(cls, data):
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if (old_password and not new_password) or (new_password and not old_password):
            raise ValueError("Both old_password and new_password must be "
                             "provided to change password")

        if old_password and new_password and old_password == new_password:
            raise ValueError("New password must be different from old password")
        return data


class LanguagePreferenceUpdate(BaseModel):
    language_preference: str = Field(..., description="Language preference ('en' or 'de')")

    @field_validator("language_preference")
    def validate_language(cls, language_code):
        if language_code not in ("en", "de"):
            raise ValueError("Language preference must be 'en' or 'de'")
        return language_code