from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str  # Auth0 user ID


class UserUpdate(BaseModel):
    """User update schema (password changes not supported with Auth0)."""
    username: Optional[str] = None
    # Password fields removed - Auth0 handles password management


class LanguagePreferenceUpdate(BaseModel):
    language_preference: str = Field(..., description="Language preference ('en' or 'de')")

    @field_validator("language_preference")
    def validate_language(cls, language_code):
        if language_code not in ("en", "de"):
            raise ValueError("Language preference must be 'en' or 'de'")
        return language_code


class PasswordUpdate(BaseModel):
    """Password update schema."""
    password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")