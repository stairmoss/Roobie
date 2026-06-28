import os
import pytest
import tempfile
import shutil
from tools.file_tools import FileTools

@pytest.fixture
def temp_workspace():
    # Setup temporary directory for workspace
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test runs
    shutil.rmtree(temp_dir)

def test_create_and_read_file(temp_workspace):
    ft = FileTools(temp_workspace)
    
    # Create file
    res = ft.create_file("test.txt", "hello test")
    assert res["success"] is True
    assert os.path.exists(os.path.join(temp_workspace, "test.txt"))
    
    # Read file
    res = ft.read_file("test.txt")
    assert res["success"] is True
    assert res["content"] == "hello test"

def test_edit_file(temp_workspace):
    ft = FileTools(temp_workspace)
    ft.create_file("test.txt", "hello original content")
    
    # Edit file
    res = ft.edit_file("test.txt", "original", "updated")
    assert res["success"] is True
    
    # Read and verify content
    read_res = ft.read_file("test.txt")
    assert read_res["content"] == "hello updated content"

def test_delete_file_and_folder(temp_workspace):
    ft = FileTools(temp_workspace)
    ft.create_file("test.txt", "some content")
    
    # Delete file
    res = ft.delete_file("test.txt")
    assert res["success"] is True
    assert not os.path.exists(os.path.join(temp_workspace, "test.txt"))
    
    # Create directory and delete it
    ft.create_folder("subfolder")
    assert os.path.exists(os.path.join(temp_workspace, "subfolder"))
    res = ft.delete_file("subfolder")
    assert res["success"] is True
    assert not os.path.exists(os.path.join(temp_workspace, "subfolder"))

def test_list_directory(temp_workspace):
    ft = FileTools(temp_workspace)
    ft.create_file("file1.txt", "content1")
    ft.create_file("file2.txt", "content2")
    ft.create_folder("subdir")
    
    res = ft.list_directory(".")
    assert res["success"] is True
    names = [entry["name"] for entry in res["entries"]]
    assert "file1.txt" in names
    assert "file2.txt" in names
    assert "subdir" in names

def test_get_tree(temp_workspace):
    ft = FileTools(temp_workspace)
    ft.create_file("file1.txt", "content1")
    ft.create_folder("subdir")
    ft.create_file("subdir/file2.txt", "content2")
    
    res = ft.get_tree(".", max_depth=2)
    assert res["success"] is True
    assert len(res["tree"]) > 0

def test_path_traversal(temp_workspace):
    ft = FileTools(temp_workspace)
    with pytest.raises(ValueError, match="Path traversal detected"):
        ft._resolve("../outside.txt")

