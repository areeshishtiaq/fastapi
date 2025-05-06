import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pytest

from main import app
from datamodel import TopicalMap, PillarPage

client = TestClient(app)

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client that will be used in tests"""
    with patch('main.client') as mock_client:
        yield mock_client

def test_generate_topical_map_success(mock_openai_client):
    """
    Test the generate-topical-map endpoint with a successful response from OpenAI
    """
    # Sample mock response from OpenAI
    mock_openai_response = {
        "money_keyword": "fat loss diet",
        "pillar_pages": [
            {
                "supporting_pages": [
                    "Understanding Macronutrients and Their Role in Fat Loss",
                    "The Importance of Portion Control and Caloric Deficit",
                    "Hydration and Its Impact on Metabolism"
                ],
                "supporting_blog_topics": [
                    "How Macronutrients Affect Fat Loss: A Beginner's Guide",
                    "Portion Control Tips for Effective Weight Management",
                    "The Role of Water in Boosting Metabolism and Weight Loss"
                ]
            },
            {
                "supporting_pages": [
                    "Incorporating Strength Training into Your Routine",
                    "The Benefits of High-Intensity Interval Training (HIIT)",
                    "Understanding Non-Exercise Activity Thermogenesis (NEAT)"
                ],
                "supporting_blog_topics": [
                    "Strength Training vs. Cardio: Which Is Better for Fat Loss?",
                    "How HIIT Accelerates Fat Burning",
                    "Simple Ways to Increase NEAT for Weight Loss"
                ]
            },
            {
                "supporting_pages": [
                    "The Role of Sleep in Fat Loss",
                    "Managing Stress to Prevent Emotional Eating",
                    "Mindful Eating Practices for Sustainable Weight Loss"
                ],
                "supporting_blog_topics": [
                    "How Sleep Deprivation Affects Weight Loss",
                    "Stress Management Techniques to Curb Emotional Eating",
                    "Mindful Eating: A Key to Long-Term Fat Loss Success"
                ]
            },
            {
                "supporting_pages": [
                    "Personalizing Your Fat Loss Diet Plan",
                    "The Importance of Tracking Progress",
                    "Adapting Your Diet as You Age"
                ],
                "supporting_blog_topics": [
                    "Creating a Customized Fat Loss Diet Plan",
                    "Why Tracking Your Progress Is Crucial for Success",
                    "Adapting Your Diet for Effective Weight Loss After 40"
                ]
            }
        ]
    }

    # Create a mock completion object
    mock_message = MagicMock()
    mock_message.content = json.dumps(mock_openai_response)
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    # Configure the mock to return our predefined response
    mock_openai_client.chat.completions.create.return_value = mock_completion

    # Make a request to our API
    response = client.post(
        "/generate-topical-map",
        json={"keyword": "fat loss diet"}
    )
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Parse the response body
    response_data = response.json()
    
    # Add debugging to see the full response
    if not response_data["success"]:
        print(f"Error message: {response_data.get('error', 'No error message')}")
    
    # Assert that the response indicates success
    assert response_data["success"] is True
    
    # Assert that the data in the response matches our mock data
    assert response_data["data"]["money_keyword"] == mock_openai_response["money_keyword"]
    
    # Verify the number of pillar pages
    assert len(response_data["data"]["pillar_pages"]) == len(mock_openai_response["pillar_pages"])
    
    # Verify the content of the first pillar page
    first_pillar = response_data["data"]["pillar_pages"][0]
    assert first_pillar["supporting_pages"] == mock_openai_response["pillar_pages"][0]["supporting_pages"]
    assert first_pillar["supporting_blog_topics"] == mock_openai_response["pillar_pages"][0]["supporting_blog_topics"]

def test_generate_topical_map_error_handling(mock_openai_client):
    """
    Test error handling in the generate-topical-map endpoint when OpenAI API fails
    """
    # Mock the OpenAI client to raise an exception
    mock_openai_client.chat.completions.create.side_effect = Exception("API error")

    # Make a request to our API
    response = client.post(
        "/generate-topical-map",
        json={"keyword": "fat loss diet"}
    )
    
    # Parse the response body
    response_data = response.json()
    
    # Assert that the response indicates failure
    assert response_data["success"] is False
    
    # Assert that there's an error message
    assert "error" in response_data
    assert "API error" in response_data["error"]

def test_generate_topical_map_invalid_json(mock_openai_client):
    """
    Test handling of invalid JSON in OpenAI response
    """
    # Create a mock response with invalid JSON
    mock_message = MagicMock()
    mock_message.content = "This is not valid JSON"
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    # Configure the mock to return the invalid JSON response
    mock_openai_client.chat.completions.create.return_value = mock_completion

    # Make a request to our API
    response = client.post(
        "/generate-topical-map",
        json={"keyword": "fat loss diet"}
    )
    
    # Parse the response body
    response_data = response.json()
    
    # Assert that the response indicates failure
    assert response_data["success"] is False
    
    # Assert that there's an error message about JSON parsing
    assert "error" in response_data
    assert "Failed to parse JSON" in response_data["error"] or "Could not find valid JSON" in response_data["error"]