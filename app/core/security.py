"""Password hashing and verification using Argon2."""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        Hashed password string.
    """
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        password: Plain text password to verify.
        password_hash: Hashed password to compare against.
        
    Returns:
        True if password matches the hash, False otherwise.
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerificationError:
        return False