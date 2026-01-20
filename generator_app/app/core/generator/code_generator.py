from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List


TYPE_MAP_SQLALCHEMY = {
    "int": "Integer",
    "str": "String",
    "float": "Float",
    "bool": "Boolean",
    "datetime": "DateTime",
    "uuid": "UUID",
}

TYPE_MAP_PYTHON = {
    "int": "int",
    "str": "str",
    "float": "float",
    "bool": "bool",
    "datetime": "datetime",
    "uuid": "UUID",
}


class CodeGenerator:
    """
    Core generator responsible for rendering templates and producing
    a complete FastAPI project structure based on a JSON definition.
    """

    def __init__(self, templates_dir: Path, output_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            # Para Python, mejor no recortar bloques.
            trim_blocks=False,
            lstrip_blocks=False,
        )
        self.output_dir = output_dir

        self.extra_routers = []
        self.extra_requirements = []
        self.extra_files = []
        self.project_def = None


    # -------------------------------------------------------------------------
    # URL builders
    # -------------------------------------------------------------------------
    @staticmethod
    def build_sync_url(db_cfg: Dict[str, Any]) -> str:
        """Build SQLAlchemy sync database URL."""
        engine = db_cfg["engine"]

        if engine == "sqlite":
            return f"sqlite:///./{db_cfg['database']}"

        return (
            f"{engine}://{db_cfg['user']}:{db_cfg['password']}"
            f"@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
        )

    @staticmethod
    def build_async_url(db_cfg: Dict[str, Any]) -> str:
        """Build SQLAlchemy async database URL."""
        engine = db_cfg["engine"]

        if engine == "postgresql":
            return (
                f"postgresql+asyncpg://{db_cfg['user']}:{db_cfg['password']}"
                f"@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
            )

        if engine == "sqlite":
            return f"sqlite+aiosqlite:///./{db_cfg['database']}"

        if engine == "mysql":
            return (
                f"mysql+aiomysql://{db_cfg['user']}:{db_cfg['password']}"
                f"@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
            )

        raise ValueError(f"Engine async no soportado: {engine}")

    # -------------------------------------------------------------------------
    # Model context builder (incluye relaciones)
    # -------------------------------------------------------------------------
    def _prepare_model_context(
        self,
        model_def: Dict[str, Any],
        model_table_map: Dict[str, str],
        global_m2m_specs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        fields: List[Dict[str, Any]] = []
        imports = set()
        has_datetime = False
        has_uuid = False
        has_foreign_keys = False

        # Tipo de PK por defecto
        pk_type = "int"

        # ------------------------------
        # Campos básicos + FKs
        # ------------------------------
        for f in model_def["fields"]:
            field_type = f["type"]

            if field_type not in TYPE_MAP_SQLALCHEMY or field_type not in TYPE_MAP_PYTHON:
                raise ValueError(f"Tipo no soportado en modelo {model_def['name']}: {field_type}")

            sa_type = TYPE_MAP_SQLALCHEMY[field_type]
            py_type = TYPE_MAP_PYTHON[field_type]

            imports.add(sa_type)

            if field_type == "datetime":
                has_datetime = True

            if field_type == "uuid":
                has_uuid = True
                if f.get("primary_key", False):
                    pk_type = "UUID"

            if f.get("primary_key", False) and field_type == "int":
                pk_type = "int"

            foreign_key = f.get("foreign_key")
            if foreign_key:
                has_foreign_keys = True

            fields.append(
                {
                    **f,
                    "sa_type": sa_type,
                    "py_type": py_type,
                    "default": f.get("default"),
                    "foreign_key": foreign_key,
                }
            )

        # ------------------------------
        # Relacionship Many-to-One
        # ------------------------------
        relationships: List[Dict[str, Any]] = []
        has_relationships = False

        for f in fields:
            rel_name = f.get("relationship")
            back_populates = f.get("back_populates")
            foreign_key = f.get("foreign_key")

            if rel_name and back_populates and foreign_key:
                # foreign_key = "stations.id" → target_table = "stations"
                target_table = foreign_key.split(".")[0]
                # Buscamos el nombre de modelo cuyo table_name coincida
                target_model = None
                for m_name, t_name in model_table_map.items():
                    if t_name == target_table:
                        target_model = m_name
                        break

                if not target_model:
                    raise ValueError(
                        f"No se encontró modelo para la foreign_key '{foreign_key}' en {model_def['name']}"
                    )

                relationships.append(
                    {
                        "name": rel_name,
                        "target": target_model,
                        "back_populates": back_populates,
                    }
                )
                has_relationships = True

        # ------------------------------
        # Relacionship Many-to-Many
        # ------------------------------
        many_to_many: List[Dict[str, Any]] = []
        has_many_to_many = False

        for rel in model_def.get("many_to_many", []):
            target = rel["target"]
            association_table = rel["association_table"]
            back_populates = rel["back_populates"]
            # nombre de atributo en este modelo
            rel_name = rel.get("name", target.lower() + "s")

            many_to_many.append(
                {
                    "name": rel_name,
                    "target": target,
                    "table_name": association_table,
                    "back_populates": back_populates,
                }
            )
            has_many_to_many = True

        many_to_many_tables: List[Dict[str, Any]] = []
        m2m_imports: List[Dict[str, Any]] = []

        for spec in global_m2m_specs:
            involved = spec["left_model"] == model_def["name"] or spec["right_model"] == model_def["name"]

            if not involved:
                continue

            if spec["owner"] == model_def["name"]:
                many_to_many_tables.append(
                    {
                        "table_name": spec["table_name"],
                        "left_key": spec["left_key"],
                        "right_key": spec["right_key"],
                        "left_fk": spec["left_fk"],
                        "right_fk": spec["right_fk"],
                    }
                )
                has_many_to_many = True
            else:
                m2m_imports.append(
                    {
                        "module": spec["owner_module"],
                        "table_name": spec["table_name"],
                    }
                )
                has_many_to_many = True

        ctx = {
            "name": model_def["name"],
            "module_name": model_def["name"].lower(),
            "description": model_def.get("description"),
            "table_name": model_def.get("table_name", model_def["name"].lower()),
            "fields": fields,
            "imports": sorted(list(imports)),
            "snake_name": model_def["name"].lower(),
            "has_datetime": has_datetime,
            "has_uuid": has_uuid,
            "pk_type": pk_type,
            "routes": model_def.get("routes", {}),

            # Relaciones
            "has_foreign_keys": has_foreign_keys,
            "has_relationships": has_relationships,
            "relationships": relationships,
            "has_many_to_many": has_many_to_many,
            "many_to_many": many_to_many,
            "many_to_many_tables": many_to_many_tables,
            "m2m_imports": m2m_imports,
        }
        return ctx

    # -------------------------------------------------------------------------
    # Template renderer
    # -------------------------------------------------------------------------
    def _render_to_file(self, template_name: str, context: Dict[str, Any], output_path: Path):
        template = self.env.get_template(template_name)
        rendered = template.render(**context)
        output_path.write_text(rendered, encoding="utf-8")

    # -------------------------------------------------------------------------
    # Main generator
    # -------------------------------------------------------------------------
    def generate_project_structure(self, project_def: Dict[str, Any], models_def: List[Dict[str, Any]]):
        """
        Generates a complete FastAPI project structure based on the project
        and model definitions.
        """

        self.project_def = project_def

        mode = project_def.get("mode", "sync")
        is_async = mode == "async"

        # Select templates based on mode
        db_template = (
            "project/db_session_async.jinja2"
            if is_async else
            "project/db_session_sync.jinja2"
        )

        router_template = (
            "routers/router_crud_async.jinja2"
            if is_async else
            "routers/router_crud_sync.jinja2"
        )

        # Build URLs
        sync_url = self.build_sync_url(project_def["database"])
        async_url = self.build_async_url(project_def["database"]) if is_async else None

        # Create folder structure
        app_dir = self.output_dir / "app"
        (app_dir / "api" / "v1" / "endpoints").mkdir(parents=True, exist_ok=True)
        (app_dir / "models").mkdir(parents=True, exist_ok=True)
        (app_dir / "schemas").mkdir(parents=True, exist_ok=True)
        (app_dir / "db").mkdir(parents=True, exist_ok=True)
        (app_dir / "core").mkdir(parents=True, exist_ok=True)

        # ---------------------------------------------------------------------
        # Mapa de modelos → table_name
        # ---------------------------------------------------------------------
        model_table_map: Dict[str, str] = {}

        if not models_def:
            models_def = []

        for m in models_def:
            model_table_map[m["name"]] = m.get("table_name", m["name"].lower())

        # ---------------------------------------------------------------------
        # Especificaciones globales Many-to-Many (tablas de asociación)
        # ---------------------------------------------------------------------    
        global_m2m_specs_dict: Dict[tuple, Dict[str, Any]] = {}

        for m in models_def:
            this_model = m["name"]
            this_table = model_table_map[this_model]
            this_snake = this_model.lower()

            for rel in m.get("many_to_many", []):
                target_model = rel["target"]
                target_table = model_table_map[target_model]
                target_snake = target_model.lower()
                association_table = rel["association_table"]

                # Clave única para esta relación (evita duplicados)
                key = (
                    association_table,
                    tuple(sorted([this_model, target_model])),
                )
                if key in global_m2m_specs_dict:
                    # Ya registrada desde el otro lado
                    continue

                # Determinamos el "owner" léxico (para definir la tabla)
                owner = min(this_model, target_model)

                if owner == this_model:
                    left_model = this_model
                    right_model = target_model
                    left_snake = this_snake
                    right_snake = target_snake
                    left_table = this_table
                    right_table = target_table
                else:
                    left_model = target_model
                    right_model = this_model
                    left_snake = target_snake
                    right_snake = this_snake
                    left_table = target_table
                    right_table = this_table

                global_m2m_specs_dict[key] = {
                    "table_name": association_table,
                    "owner": owner,
                    "owner_module": owner.lower(),
                    "left_model": left_model,
                    "right_model": right_model,
                    "left_key": f"{left_snake}_id",
                    "right_key": f"{right_snake}_id",
                    "left_fk": f"{left_table}.id",
                    "right_fk": f"{right_table}.id",
                }

        global_m2m_specs: List[Dict[str, Any]] = list(global_m2m_specs_dict.values())


        # ---------------------------------------------------------------------
        # Core config (Pydantic settings)
        # ---------------------------------------------------------------------
        config_context = {
            "project": {
                **project_def,
                "database_url": async_url if is_async and async_url else sync_url,
            }
        }
        self._render_to_file(
            "project/config.jinja2",
            config_context,
            app_dir / "core" / "config.py",
        )

        # ---------------------------------------------------------------------
        # DB session
        # ---------------------------------------------------------------------
        self._render_to_file(
            db_template,
            {
                "database_url": sync_url,
                "async_database_url": async_url,
            },
            app_dir / "db" / "session.py",
        )

        # Base class
        self._render_to_file(
            "project/db_base_class.jinja2",
            {},
            app_dir / "db" / "base_class.py",
        )

        routers_info = []

        # ---------------------------------------------------------------------
        # Models, schemas, routers
        # ---------------------------------------------------------------------
        for model_def in models_def:
            model_ctx = self._prepare_model_context(model_def, model_table_map, global_m2m_specs)

            # Model
            self._render_to_file(
                "models/sqlalchemy_model.jinja2",
                {"model": model_ctx},
                app_dir / "models" / f"{model_ctx['module_name']}.py",
            )

            # Schema
            self._render_to_file(
                "schemas/pydantic_schema.jinja2",
                {"model": model_ctx},
                app_dir / "schemas" / f"{model_ctx['module_name']}.py",
            )

            # Router
            if model_ctx["routes"].get("generate_crud", True):
                router_module_name = f"{model_ctx['module_name']}_router"
                router_file = app_dir / "api" / "v1" / "endpoints" / f"{router_module_name}.py"

                self._render_to_file(
                    router_template,
                    {"model": model_ctx},
                    router_file,
                )

                routers_info.append(
                    {
                        "router_name": "router",
                        "module": router_module_name,
                        "prefix": model_ctx["routes"].get(
                            "prefix",
                            f"/{model_ctx['module_name']}s",
                        ),
                        "tags": model_ctx["routes"].get("tags", [model_ctx["name"]]),
                    }
                )


        # ---------------------------------------------------------------------
        # Load and execute modules
        # ---------------------------------------------------------------------
        from generator_app.app.core.generator.module_loader import ModuleLoader

        loader = ModuleLoader(self.env, self.output_dir, project_def)
        modules = loader.load_modules()

        for module in modules:
            result = module.generate()

            # Routers
            for r in result.get("routers", []):
                self.extra_routers.append(r)

            # Requirements
            for req in result.get("requirements", []):
                self.extra_requirements.append(req)

            # Extra files (if any)
                for f in result.get("extra_files", []):
                    pass  # future use

        # ---------------------------------------------------------------------
        # Main app
        # ---------------------------------------------------------------------
        self._render_to_file(
            "project/main_app.jinja2",
            {
                "project": project_def,
                "routers": routers_info,
                "routers_imports": [r["module"] for r in routers_info],
                "extra_routers": self.extra_routers,
            },
            app_dir / "main.py",
        )

        # ---------------------------------------------------------------------
        # run.py (ejecución rápida)
        # ---------------------------------------------------------------------
        self._render_to_file(
            "project/run.jinja2",
            {},
            self.output_dir / "run.py",
        )

        # ---------------------------------------------------------------------
        # Requirements
        # ---------------------------------------------------------------------
        requirements = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "pydantic-settings",
        ]

        requirements.extend(self.extra_requirements)

        if is_async:
            engine = project_def["database"]["engine"]
            if engine == "postgresql":
                requirements.append("asyncpg")
            elif engine == "sqlite":
                requirements.append("aiosqlite")
            elif engine == "mysql":
                requirements.append("aiomysql")

        (self.output_dir / "requirements.txt").write_text(
            "\n".join(requirements) + "\n",
            encoding="utf-8",
        )
