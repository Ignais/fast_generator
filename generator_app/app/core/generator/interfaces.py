from abc import ABC, abstractmethod
from pathlib import Path
from jinja2 import Environment
from typing import Dict, Any

class BaseModuleGenerator(ABC):
    """
    Interface for all pluggable modules (Auth, Ecommerce, ERP, etc.)
    """

    def __init__(self, env: Environment, output_dir: Path, project_def: Dict[str, Any], module_config: Dict[str, Any]):
        self.env = env
        self.output_dir = output_dir
        self.project_def = project_def
        self.module_config = module_config

    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """
        Generates the module and returns:
        {
            "routers": [...],
            "requirements": [...],
            "extra_files": [...]
        }
        """
        pass
