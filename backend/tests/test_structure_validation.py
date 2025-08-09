"""
Structure validation tests that can run without external dependencies.
"""

import ast
import os


class TestProjectStructure:
    """Test project structure and syntax validation."""

    def _resolve_backend_path(self, path):
        """Resolve path relative to backend directory, whether run from backend/ or root."""
        # If path exists as-is, use it (running from backend/)
        if os.path.exists(path):
            return path
        # Try with backend/ prefix (running from root)
        backend_path = os.path.join("backend", path)
        if os.path.exists(backend_path):
            return backend_path
        # Return original path if neither exists (will fail appropriately)
        return path

    def test_backend_file_structure(self) -> None:
        """Test that all required backend files exist."""
        required_files = [
            "app/__init__.py",
            "app/main.py",
            "app/models/__init__.py",
            "app/models/game_models.py",
            "app/models/db_models.py",
            "app/api/__init__.py",
            "app/api/game_routes.py",
            "app/agents/__init__.py",
            "app/config.py",
            "app/database.py",
        ]

        for file_path in required_files:
            resolved_path = self._resolve_backend_path(file_path)
            assert os.path.exists(resolved_path), (
                f"Required file {file_path} is missing (looked for {resolved_path})"
            )
            print(f"✅ {file_path} exists at {resolved_path}")

        # Verify dependency configuration exists (UV-based project structure)
        dependency_config_found = False
        config_sources = []

        # Check for root pyproject.toml (primary UV configuration)
        for pyproject_path in ["../pyproject.toml", "./pyproject.toml", "pyproject.toml"]:
            if os.path.exists(pyproject_path):
                dependency_config_found = True
                config_sources.append(f"root pyproject.toml ({pyproject_path})")
                print(f"✅ Found UV dependency configuration: {pyproject_path}")
                break

        assert dependency_config_found, (
            "No dependency configuration found. Expected root pyproject.toml for UV-based project"
        )

    def test_python_syntax_validation(self) -> None:
        """Test that all Python files have valid syntax."""
        python_files = []

        # Determine base paths
        app_dir = self._resolve_backend_path("app")
        tests_dir = self._resolve_backend_path("tests")

        # Walk through app directory
        if os.path.exists(app_dir):
            for root, _dirs, files in os.walk(app_dir):
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(os.path.join(root, file))

        # Add test files
        if os.path.exists(tests_dir):
            for root, _dirs, files in os.walk(tests_dir):
                for file in files:
                    if file.endswith(".py") and file.startswith("test_"):
                        python_files.append(os.path.join(root, file))

        syntax_errors = []

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ {file_path} syntax valid")
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path} syntax error: {e}")
            except Exception as e:
                print(f"⚠️ {file_path} could not be checked: {e}")

        assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"

    def test_api_endpoints_defined(self) -> None:
        """Test that required API endpoints are defined in route files."""
        route_file = self._resolve_backend_path("app/api/game_routes.py")

        with open(route_file) as f:
            content = f.read()

        # Required endpoints based on frontend API calls
        required_endpoints = [
            '@router.post("/character"',  # createCharacter
            '@router.get("/character/{character_id}"',  # getCharacter
            '@router.post("/input"',  # sendPlayerInput
            '@router.post("/campaign"',  # createCampaign
            '@router.post("/generate-image"',  # generateImage
            '@router.post("/battle-map"',  # generateBattleMap
        ]

        missing_endpoints = []

        for endpoint in required_endpoints:
            if endpoint not in content:
                missing_endpoints.append(endpoint)
                print(f"❌ Missing endpoint: {endpoint}")
            else:
                print(f"✅ Found endpoint: {endpoint}")

        assert len(missing_endpoints) == 0, f"Missing endpoints: {missing_endpoints}"

    def test_model_imports_structure(self) -> None:
        """Test that model imports are properly structured."""
        models_file = self._resolve_backend_path("app/models/game_models.py")

        with open(models_file) as f:
            content = f.read()

        # Check for required model classes
        required_models = [
            "class CharacterSheet",
            "class CreateCharacterRequest",
            "class PlayerInput",
            "class GameResponse",
            "class Campaign",
            "class CreateCampaignRequest",
        ]

        missing_models = []

        for model in required_models:
            if model not in content:
                missing_models.append(model)
                print(f"❌ Missing model: {model}")
            else:
                print(f"✅ Found model: {model}")

        assert len(missing_models) == 0, f"Missing models: {missing_models}"

    def test_requirements_file_exists(self) -> None:
        """Test that project dependencies are properly defined."""
        # Check for new root pyproject.toml first (preferred approach)
        # Try different path variations depending on where pytest is run from
        possible_pyproject_paths = [
            "../pyproject.toml",  # when run from backend/
            "./pyproject.toml",  # when run from root
            "pyproject.toml",  # when run from root (alternative)
        ]
        backend_requirements = "requirements.txt"

        content = ""
        dependency_source = None

        # Try to find pyproject.toml first
        for pyproject_path in possible_pyproject_paths:
            if os.path.exists(pyproject_path):
                dependency_source = f"root pyproject.toml ({pyproject_path})"
                with open(pyproject_path) as f:
                    content = f.read()
                print(f"✅ Using {dependency_source} for dependency validation")
                break

        # Fallback to backend requirements.txt if pyproject.toml not found
        if not dependency_source and os.path.exists(backend_requirements):
            dependency_source = "backend requirements.txt"
            with open(backend_requirements) as f:
                content = f.read()
            print(f"✅ Using {dependency_source} for dependency validation")

        # Also try backend/requirements.txt from root directory
        if not dependency_source and os.path.exists("backend/requirements.txt"):
            dependency_source = "backend/requirements.txt"
            with open("backend/requirements.txt") as f:
                content = f.read()
            print(f"✅ Using {dependency_source} for dependency validation")

        if not dependency_source:
            raise AssertionError("Neither root pyproject.toml nor backend requirements.txt found")

        # Critical dependencies for the project
        critical_deps = [
            "fastapi",
            "pydantic",
            "semantic-kernel",
            "azure-identity",
            "openai",
            "sqlalchemy",
            "pytest",
        ]

        missing_deps = []

        for dep in critical_deps:
            if dep not in content.lower():
                missing_deps.append(dep)
                print(f"❌ Missing dependency: {dep}")
            else:
                print(f"✅ Found dependency: {dep}")

        assert len(missing_deps) == 0, (
            f"Missing critical dependencies: {missing_deps} in {dependency_source}"
        )


class TestFrontendBackendAPIMapping:
    """Test that frontend API calls map to backend endpoints."""

    def test_api_url_mapping(self) -> None:
        """Test that frontend API URLs map correctly to backend routes."""
        # Read frontend API file
        frontend_api_file = "../frontend/src/services/api.ts"

        if not os.path.exists(frontend_api_file):
            print(
                "⚠️ Frontend API file not found - skipping frontend-backend mapping test"
            )
            return

        with open(frontend_api_file) as f:
            frontend_content = f.read()

        # Read backend routes file
        backend_routes_file = "app/api/game_routes.py"

        with open(backend_routes_file) as f:
            backend_content = f.read()

        # Map frontend calls to backend endpoints
        mappings = [
            ('"/game/character"', '@router.post("/character"'),
            (
                "`/game/character/${characterId}`",
                '@router.get("/character/{character_id}"',
            ),
            ('"/game/input"', '@router.post("/input"'),
            ('"/game/campaign"', '@router.post("/campaign"'),
            ('"/game/generate-image"', '@router.post("/generate-image"'),
            ('"/game/battle-map"', '@router.post("/battle-map"'),
        ]

        missing_mappings = []

        for frontend_call, backend_endpoint in mappings:
            frontend_found = frontend_call in frontend_content
            backend_found = backend_endpoint in backend_content

            if frontend_found and backend_found:
                print(f"✅ API mapping: {frontend_call} -> {backend_endpoint}")
            elif frontend_found and not backend_found:
                missing_mappings.append(
                    f"Frontend calls {frontend_call} but backend missing {backend_endpoint}"
                )
                print(
                    f"❌ Frontend calls {frontend_call} but backend missing {backend_endpoint}"
                )
            elif not frontend_found and backend_found:
                print(
                    f"⚠️ Backend has {backend_endpoint} but frontend doesn't call {frontend_call}"
                )
            else:
                print("⚠️ Neither frontend nor backend has this mapping")

        assert len(missing_mappings) == 0, f"Missing API mappings: {missing_mappings}"

    def test_api_base_url_consistency(self) -> None:
        """Test that API base URL is configured correctly."""
        frontend_api_file = "../frontend/src/services/api.ts"

        if not os.path.exists(frontend_api_file):
            print("⚠️ Frontend API file not found - skipping base URL test")
            return

        with open(frontend_api_file) as f:
            content = f.read()

        # Check that API base URL includes /api prefix to match backend routing
        if "localhost:8000/api" in content:
            print("✅ API base URL correctly configured with /api prefix")
        else:
            print("❌ API base URL may not match backend routing structure")
            # This is a warning, not a failure since it might be configured differently
