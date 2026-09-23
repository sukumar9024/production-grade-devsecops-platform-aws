from app.core.security import (
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plaintext():
    password = "SecurePassword123!"

    password_hash = hash_password(
        password
    )

    assert password_hash != password

    assert password_hash.startswith(
        "$argon2"
    )


def test_correct_password_verifies():
    password = "SecurePassword123!"

    password_hash = hash_password(
        password
    )

    assert verify_password(
        password,
        password_hash,
    )


def test_wrong_password_fails():
    password_hash = hash_password(
        "SecurePassword123!"
    )

    assert not verify_password(
        "WrongPassword123!",
        password_hash,
    )