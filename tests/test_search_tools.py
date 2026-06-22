import pytest
from unittest.mock import patch, MagicMock
from tools.search_tools import SearchTools

@patch("requests.get")
def test_web_search_ddg_html(mock_get):
    # Mock DuckDuckGo HTML response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <div class="result">
        <a class="result__a" href="https://example.com/site">Example Domain</a>
        <a class="result__snippet">This is a snippet about example domain.</a>
    </div>
    """
    mock_get.return_value = mock_response
    
    st = SearchTools()
    res = st.web_search("example")
    
    assert res["success"] is True
    assert len(res["results"]) == 1
    assert res["results"][0]["title"] == "Example Domain"
    assert res["results"][0]["url"] == "https://example.com/site"
    assert res["results"][0]["snippet"] == "This is a snippet about example domain."

@patch("requests.get")
def test_fetch_url(mock_get):
    # Mock website response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <head><title>Test Title</title></head>
        <body>
            <script>alert('hello');</script>
            <style>body { color: red; }</style>
            <h1>Hello World</h1>
            <p>This is a test paragraph.</p>
        </body>
    </html>
    """
    mock_get.return_value = mock_response
    
    st = SearchTools()
    res = st.fetch_url("https://example.com")
    
    assert res["success"] is True
    assert "Hello World" in res["content"]
    assert "This is a test paragraph." in res["content"]
    assert "alert" not in res["content"]  # scripts should be stripped
    assert "body {" not in res["content"]  # style should be stripped
