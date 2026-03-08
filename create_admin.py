#!/usr/bin/env python3
"""Create or update VoxCore developer admin credentials in .env."""

import os
import secrets
import string
import sys


def _generate_secret(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _upsert_env_var(content: str, key: str, value: str) -> str:
    lines = content.splitlines()
    replaced = False
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = f"{key}={value}"
            replaced = True
            break
    if not replaced:
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def create_admin_account(username: str, password: str, env_path: str) -> None:
    print("\n" + "=" * 80)
    print("VoxCore Admin/God Account Setup")
    print("=" * 80 + "\n")

    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as infile:
            env_content = infile.read()
    else:
        env_content = ""

    jwt_secret = _generate_secret(64)
    env_content = _upsert_env_var(env_content, "VOXCORE_ADMIN_USERNAME", username)
    env_content = _upsert_env_var(env_content, "VOXCORE_ADMIN_PASSWORD", password)
    env_content = _upsert_env_var(env_content, "SECRET_KEY", jwt_secret)

    with open(env_path, "w", encoding="utf-8") as outfile:
        outfile.write(env_content)

    print("✅ Admin/God account configured successfully\n")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Env file: {env_path}")
    print("\n⚠️  Restart backend after this change to reload environment variables.")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "VoxCore123!"

    repo_root = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(repo_root, "voxcore", "voxquery", ".env")
    create_admin_account(username, password, env_file)
