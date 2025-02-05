# test/test_middleware.py
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app  # Import the FastAPI app instance
import pytest
import requests
from requests.exceptions import Timeout

# Initialize Test Client
client = TestClient(app)

# Test Constants
VALID_HEADERS = {
    "Content-Type": "text/plain",
    "X-Requirements-Doc": "https://sootra-temp-folder.s3.us-east-2.amazonaws.com/Email+Quality+Assurance+Requirement+Document.docx",  # Replace with a valid test URL
}

VALID_HTML = "<html><body><h1>Test HTML</h1></body></html>"
INVALID_HTML = ""
VALID_JSON = '{"requirementsForm": {"key": "value"}}'
INVALID_JSON = '{"requirementsForm": {"key": value}}'

# Helper Functions for Payloads
def valid_payload():
    return f"{VALID_HTML}\n\n{VALID_JSON}"

def broken_json_payload():
    # A broken JSON where a closing brace is missing
    return '{"key": "value"'

def valid_json_payload():
    return {
        "key1": "value1",
        "key2": "value2",
        "key3": {"nestedKey": "nestedValue"}
    }

def invalid_html_payload():
    return "<html><body><h1>Invalid HTML without closing tags"






def test_accessibility_part1_valid():
    payload = valid_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers=VALID_HEADERS
    )
    assert response.status_code == 200, f"Unexpected error: {response.json()}"
    assert "results" in response.json(), "Response does not contain 'results'."

def test_accessibility_part1_internal_server_error():
    payload = "<html><body><h1>Test</h1></body></html>"

    # Mocking a function to raise an exception
    with patch("main.preprocess_text_for_llm", side_effect=Exception("Unexpected error")):
        response = client.post(
            "/accessibility_part1",
            data=payload,
            headers=VALID_HEADERS
        )
    
    assert response.status_code == 500, "Expected 500 Internal Server Error"
    assert "Error processing accessibility part 1" in response.json()["detail"], "Expected error message"

def test_accessibility_part1_broken_json():
    payload = broken_json_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers=VALID_HEADERS
    )
    assert response.status_code == 400, f"Unexpected error: {response.json()}"
    assert "detail" in response.json(), "Response does not contain 'detail'."

def test_accessibility_part1_valid_json():
    payload = valid_json_payload()
    response = client.post(
        "/accessibility_part1",
        json=payload,  # Sending as JSON instead of data
        headers=VALID_HEADERS
    )
    
    assert response.status_code == 200, f"Unexpected error: {response.json()}"
    assert "results" in response.json(), "Response does not contain 'results'."
    assert isinstance(response.json()["results"], dict), "Results should be a dictionary."

def test_accessibility_part1_empty_payload():
    payload = ""  # Empty request body
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers=VALID_HEADERS
    )
    assert response.status_code == 400, f"Unexpected error: {response.json()}"
    assert "detail" in response.json(), "No error detail returned for empty payload."

def test_accessibility_part1_large_payload():
    large_json = {"key": "A" * 10**6}  # 1MB JSON data
    response = client.post(
        "/accessibility_part1",
        json=large_json,
        headers=VALID_HEADERS
    )
    assert response.status_code in [413, 500], f"Unexpected error: {response.json()}"
def test_accessibility_part1_missing_headers():
    payload = valid_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload, 
        headers={}  # No headers
    )
    assert response.status_code == 400, f"Unexpected error: {response.json()}"

def test_accessibility_part1_invalid_content_type():
    payload = valid_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers={"Content-Type": "text/plain"}  # Incorrect format
    )
    assert response.status_code == 415, f"Unexpected error: {response.json()}"

def test_accessibility_part1_invalid_html():
    payload = invalid_html_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers=VALID_HEADERS
    )
    assert response.status_code == 400, f"Unexpected error: {response.json()}"
    assert "error" in response.json(), "Response does not contain expected error message."

def half_html_payload():
    return "<html><head><title>Test Page</title></head><body><h1>Header"  # Missing closing tags

def test_accessibility_part1_half_html():
    payload = half_html_payload()
    response = client.post(
        "/accessibility_part1",
        data=payload,
        headers=VALID_HEADERS
    )
    assert response.status_code == 400, f"Unexpected error: {response.json()}"
    assert "error" in response.json(), "Expected error message in response"



