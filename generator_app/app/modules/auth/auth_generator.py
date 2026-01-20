from pathlib import Path
from generator_app.app.core.generator.interfaces import BaseModuleGenerator

class AuthGenerator(BaseModuleGenerator):

    def generate(self):
        auth_dir = self.output_dir / "app" / "auth"
        (auth_dir / "models").mkdir(parents=True, exist_ok=True)
        (auth_dir / "schemas").mkdir(parents=True, exist_ok=True)
        (auth_dir / "routers").mkdir(parents=True, exist_ok=True)
        (auth_dir / "security").mkdir(parents=True, exist_ok=True)

        # -------------------------
        # MODELS
        # -------------------------
        self._render("models/user.jinja2", auth_dir / "models" / "user.py")

        if self.module_config.get("role_based", True):
            self._render("models/role.jinja2", auth_dir / "models" / "role.py")

        if self.module_config.get("permission_based", True):
            self._render("models/permission.jinja2", auth_dir / "models" / "permission.py")

        if self.module_config.get("multi_session", True):
            self._render("models/session.jinja2", auth_dir / "models" / "session.py")

        # -------------------------
        # SCHEMAS
        # -------------------------
        self._render("schemas/user.jinja2", auth_dir / "schemas" / "user.py")
        self._render("schemas/token.jinja2", auth_dir / "schemas" / "token.py")

        if self.module_config.get("role_based", True):
            self._render("schemas/role.jinja2", auth_dir / "schemas" / "role.py")

        if self.module_config.get("permission_based", True):
            self._render("schemas/permission.jinja2", auth_dir / "schemas" / "permission.py")

        if self.module_config.get("multi_session", True):
            self._render("schemas/session.jinja2", auth_dir / "schemas" / "session.py")

        # -------------------------
        # SECURITY
        # -------------------------
        self._render("security/security.jinja2", auth_dir / "security" / "security.py")

        # utils opcional
        utils_template = "security/utils.jinja2"
        if (self.env.loader.searchpath and 
            (Path(self.env.loader.searchpath[0]) / utils_template).exists()):
            self._render(utils_template, auth_dir / "security" / "utils.py")

        # -------------------------
        # ROUTERS
        # -------------------------
        self._render("routers/auth_router.jinja2", auth_dir / "routers" / "auth_router.py")

        # -------------------------
        # RETURN INTEGRATION INFO
        # -------------------------
        return {
            "routers": [
                {
                    "module": "app.auth.routers.auth_router",
                    "router_name": "router",
                    "prefix": "/auth",
                    "tags": ["Auth"]
                }
            ],
            "requirements": [
                "python-jose",
                "passlib[bcrypt]",
                "pydantic[email]"
            ],
            "extra_files": []
        }

    def _render(self, template_name, output_path):
        template = self.env.get_template(template_name)
        output_path.write_text(
            template.render(
                auth=self.module_config,
                project=self.project_def
            ),
            encoding="utf-8"
        )
