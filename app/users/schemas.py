from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    id: int

    class Config:
        from_attributes = True


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