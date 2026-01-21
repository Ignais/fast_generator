"""Seed admin role, permissions and admin user

Revision ID: ef3c1051f7e0
Revises: b12c0f01f21d
Create Date: 2026-01-21 13:13:01.453412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from uuid import uuid4
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# revision identifiers, used by Alembic.
revision: str = 'ef3c1051f7e0'
down_revision: Union[str, Sequence[str], None] = 'b12c0f01f21d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # 1. Crear permisos base
    permissions = [
        "admin:manage",
        "project:create",
        "project:update",
        "project:delete",
        "project:view",
        "user:create",
        "user:update",
        "user:delete",
        "user:view",
    ]

    permission_ids = {}

    for code in permissions:
        existing = session.execute(
            sa.text("SELECT id FROM permissions WHERE code = :code"),
            {"code": code}
        ).fetchone()

        if not existing:
            new_id = str(uuid4())
            session.execute(
                sa.text("""
                    INSERT INTO permissions (id, code, description)
                    VALUES (:id, :code, :description)
                """),
                {"id": new_id, "code": code, "description": code}
            )
            permission_ids[code] = new_id
        else:
            permission_ids[code] = existing[0]

    # 2. Crear rol admin
    admin_role = session.execute(
        sa.text("SELECT id FROM roles WHERE name = 'admin'")
    ).fetchone()

    if not admin_role:
        admin_role_id = str(uuid4())
        session.execute(
            sa.text("""
                INSERT INTO roles (id, name, description, is_default)
                VALUES (:id, 'admin', 'Administrator role', false)
            """),
            {"id": admin_role_id}
        )
    else:
        admin_role_id = admin_role[0]

    # 3. Asignar permisos al rol admin
    for perm_id in permission_ids.values():
        exists = session.execute(
            sa.text("""
                SELECT 1 FROM role_permissions
                WHERE role_id = :role_id AND permission_id = :perm_id
            """),
            {"role_id": admin_role_id, "perm_id": perm_id}
        ).fetchone()

        if not exists:
            session.execute(
                sa.text("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :perm_id)
                """),
                {"role_id": admin_role_id, "perm_id": perm_id}
            )

    # 4. Crear usuario administrador inicial
    admin_user = session.execute(
        sa.text("SELECT id FROM users WHERE email = 'admin@example.com'")
    ).fetchone()

    if not admin_user:
        session.execute(
            sa.text("""
                INSERT INTO users (id, email, hashed_password, role_id)
                VALUES (:id, :email, :password, :role_id)
            """),
            {
                "id": str(uuid4()),
                "email": "admin@example.com",
                "password": pwd_context.hash("admin123"),
                "role_id": admin_role_id
            }
        )

    session.commit()


def downgrade():
    pass
