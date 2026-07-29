import os
import tempfile
from pathlib import Path
import pytest
from managers.asset_manager import AssetManager

@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

@pytest.fixture
def dummy_image():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake image content")
        path = f.name
    yield path
    os.remove(path)

def test_import_asset(project_dir, dummy_image):
    manager = AssetManager(project_dir)
    asset = manager.import_asset(dummy_image)
    
    assert asset is not None
    assert asset.name == Path(dummy_image).stem
    assert asset.type == "image"
    
    assets = manager.get_all_assets()
    assert len(assets) == 1

def test_duplicate_import(project_dir, dummy_image):
    manager = AssetManager(project_dir)
    asset1 = manager.import_asset(dummy_image)
    asset2 = manager.import_asset(dummy_image)
    
    # Should not duplicate in db
    assert asset1.id == asset2.id
    assets = manager.get_all_assets()
    assert len(assets) == 1

def test_delete_asset(project_dir, dummy_image):
    manager = AssetManager(project_dir)
    asset = manager.import_asset(dummy_image)
    
    manager.delete_asset(asset.id)
    assets = manager.get_all_assets()
    assert len(assets) == 0
