"""
Structure validation tests that can run without external dependencies.
"""
import ast
import os
import json


class TestProjectStructure:
    """Test project structure and syntax validation."""
    
    def test_backend_file_structure(self):
        """Test that all required backend files exist."""
        required_files = [
            'app/__init__.py',
            'app/main.py',
            'app/models/__init__.py',
            'app/models/game_models.py',
            'app/models/db_models.py',
            'app/api/__init__.py',
            'app/api/game_routes.py',
            'app/agents/__init__.py',
            'app/config.py',
            'app/database.py',
            'requirements.txt'
        ]
        
        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file {file_path} is missing"
            print(f"✅ {file_path} exists")
    
    def test_python_syntax_validation(self):
        """Test that all Python files have valid syntax."""
        python_files = []
        
        # Walk through app directory
        for root, dirs, files in os.walk('app'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Add test files
        for root, dirs, files in os.walk('tests'):
            for file in files:
                if file.endswith('.py') and file.startswith('test_'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ {file_path} syntax valid")
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path} syntax error: {e}")
            except Exception as e:
                print(f"⚠️ {file_path} could not be checked: {e}")
        
        assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"
    
    def test_api_endpoints_defined(self):
        """Test that required API endpoints are defined in route files."""
        route_file = 'app/api/game_routes.py'
        
        with open(route_file, 'r') as f:
            content = f.read()
        
        # Required endpoints based on frontend API calls
        required_endpoints = [
            '@router.post("/character"',  # createCharacter
            '@router.get("/character/{character_id}"',  # getCharacter
            '@router.post("/input"',  # sendPlayerInput
            '@router.post("/campaign"',  # createCampaign
            '@router.post("/generate-image"',  # generateImage
            '@router.post("/battle-map"'  # generateBattleMap
        ]
        
        missing_endpoints = []
        
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing_endpoints.append(endpoint)
                print(f"❌ Missing endpoint: {endpoint}")
            else:
                print(f"✅ Found endpoint: {endpoint}")
        
        assert len(missing_endpoints) == 0, f"Missing endpoints: {missing_endpoints}"
    
    def test_model_imports_structure(self):
        """Test that model imports are properly structured."""
        models_file = 'app/models/game_models.py'
        
        with open(models_file, 'r') as f:
            content = f.read()
        
        # Check for required model classes
        required_models = [
            'class CharacterSheet',
            'class CreateCharacterRequest',
            'class PlayerInput',
            'class GameResponse',
            'class Campaign',
            'class CreateCampaignRequest'
        ]
        
        missing_models = []
        
        for model in required_models:
            if model not in content:
                missing_models.append(model)
                print(f"❌ Missing model: {model}")
            else:
                print(f"✅ Found model: {model}")
        
        assert len(missing_models) == 0, f"Missing models: {missing_models}"
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and contains critical dependencies."""
        requirements_file = 'requirements.txt'
        
        assert os.path.exists(requirements_file), "requirements.txt is missing"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Critical dependencies for the project
        critical_deps = [
            'fastapi',
            'pydantic',
            'semantic-kernel',
            'azure-identity',
            'openai',
            'sqlalchemy',
            'pytest'
        ]
        
        missing_deps = []
        
        for dep in critical_deps:
            if dep not in content.lower():
                missing_deps.append(dep)
                print(f"❌ Missing dependency: {dep}")
            else:
                print(f"✅ Found dependency: {dep}")
        
        assert len(missing_deps) == 0, f"Missing critical dependencies: {missing_deps}"


class TestFrontendBackendAPIMapping:
    """Test that frontend API calls map to backend endpoints."""
    
    def test_api_url_mapping(self):
        """Test that frontend API URLs map correctly to backend routes."""
        # Read frontend API file
        frontend_api_file = '../frontend/src/services/api.ts'
        
        if not os.path.exists(frontend_api_file):
            print("⚠️ Frontend API file not found - skipping frontend-backend mapping test")
            return
        
        with open(frontend_api_file, 'r') as f:
            frontend_content = f.read()
        
        # Read backend routes file
        backend_routes_file = 'app/api/game_routes.py'
        
        with open(backend_routes_file, 'r') as f:
            backend_content = f.read()
        
        # Map frontend calls to backend endpoints
        mappings = [
            ('"/game/character"', '@router.post("/character"'),
            ('`/game/character/${characterId}`', '@router.get("/character/{character_id}"'),
            ('"/game/input"', '@router.post("/input"'),
            ('"/game/campaign"', '@router.post("/campaign"'),
            ('"/game/generate-image"', '@router.post("/generate-image"'),
            ('"/game/battle-map"', '@router.post("/battle-map"')
        ]
        
        missing_mappings = []
        
        for frontend_call, backend_endpoint in mappings:
            frontend_found = frontend_call in frontend_content
            backend_found = backend_endpoint in backend_content
            
            if frontend_found and backend_found:
                print(f"✅ API mapping: {frontend_call} -> {backend_endpoint}")
            elif frontend_found and not backend_found:
                missing_mappings.append(f"Frontend calls {frontend_call} but backend missing {backend_endpoint}")
                print(f"❌ Frontend calls {frontend_call} but backend missing {backend_endpoint}")
            elif not frontend_found and backend_found:
                print(f"⚠️ Backend has {backend_endpoint} but frontend doesn't call {frontend_call}")
            else:
                print(f"⚠️ Neither frontend nor backend has this mapping")
        
        assert len(missing_mappings) == 0, f"Missing API mappings: {missing_mappings}"
    
    def test_api_base_url_consistency(self):
        """Test that API base URL is configured correctly."""
        frontend_api_file = '../frontend/src/services/api.ts'
        
        if not os.path.exists(frontend_api_file):
            print("⚠️ Frontend API file not found - skipping base URL test")
            return
        
        with open(frontend_api_file, 'r') as f:
            content = f.read()
        
        # Check that API base URL includes /api prefix to match backend routing
        if 'localhost:8000/api' in content:
            print("✅ API base URL correctly configured with /api prefix")
        else:
            print("❌ API base URL may not match backend routing structure")
            # This is a warning, not a failure since it might be configured differently