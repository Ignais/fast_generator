from typing import List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from generator_app.app.core.generator.interfaces import BaseModuleGenerator

class ModuleLoader:
    """
    Loads and executes modules based on project_def["modules"].
    """

    def __init__(self, core_env, output_dir, project_def):
        self.core_env = core_env
        self.output_dir = output_dir
        self.project_def = project_def

    def load_modules(self) -> List[BaseModuleGenerator]:
        modules = []
        modules_config = self.project_def.get("modules", {})

        # AUTH MODULE
        if modules_config.get("auth", {}).get("enabled"):
            from generator_app.app.modules.auth.auth_generator import AuthGenerator

            auth_templates = Path("app/modules/auth/templates")
            auth_env = Environment(
                loader=FileSystemLoader(str(auth_templates)),
                autoescape=False,
                trim_blocks=False,
                lstrip_blocks=False,
            )

            modules.append(
                AuthGenerator(
                    env=auth_env,
                    output_dir=self.output_dir,
                    project_def=self.project_def,
                    module_config=modules_config["auth"]
                )
            )

        return modules
