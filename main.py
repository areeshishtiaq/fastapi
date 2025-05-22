import json
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from datamodel import TopicalMap, PillarPage
from prompts import TOPICAL_MAP_PROMPT, FRIENDLY_META_TAGS_PROMPT

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Topical Map Generator API")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add a simple home page route


@app.get("/", response_class=HTMLResponse)
async def home():
    return {"message": "Hello World"}


class KeywordRequest(BaseModel):
    keyword: str


class MetaTagsRequest(BaseModel):
    primary_keyword: str
    secondary_keyword: str
    brand_name: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def parse_json_to_topical_map(json_data: Dict[str, Any]) -> TopicalMap:
    """
    Parse JSON data into a TopicalMap object.

    Args:
        json_data: A dictionary containing the JSON data

    Returns:
        TopicalMap: A populated TopicalMap object
    """
    # Create TopicalMap with the money keyword
    topical_map = TopicalMap(json_data.get("money_keyword", ""))

    # Process pillar pages if they exist
    pillar_pages_data = json_data.get("pillar_pages", [])
    for pillar_page_data in pillar_pages_data:
        # Create PillarPage object
        pillar_page = PillarPage(
            title=pillar_page_data.get("title", ""),
            supporting_pages=pillar_page_data.get("supporting_pages", []),
            supporting_blog_topics=pillar_page_data.get(
                "supporting_blog_topics", [])
        )
        # Add to topical map
        topical_map.add_topic(pillar_page)

    return topical_map


@app.post("/generate-topical-map", response_model=ApiResponse)
async def generate_topical_map(request: KeywordRequest) -> ApiResponse:
    try:
        # Replace [keyword] in the prompt with the user-provided keyword
        customized_prompt = TOPICAL_MAP_PROMPT.replace("[keyword]", request.keyword)

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # You can change this to the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates topical maps in the specified JSON format."},
                {"role": "user", "content": customized_prompt}
            ],
            temperature=0.7,
        )        # Extract response content
        content = response.choices[0].message.content
        if content is None:
            return ApiResponse(
                success=False,
                error="No content returned from the API"
            )

        # Try to find and extract JSON from the response
        try:
            # Find JSON content (in case there's additional text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                json_data = json.loads(json_content)

                # Parse the JSON into our data model
                topical_map = parse_json_to_topical_map(json_data)

                # Convert to dict for response
                result = {
                    "money_keyword": topical_map.money_keyword,
                    "pillar_pages": [
                        {
                            "title": pillar.title,
                            "supporting_pages": pillar.supporting_pages,
                            "supporting_blog_topics": pillar.supporting_blog_topics
                        } for pillar in topical_map.pillar_pages                    ]
                }

                return ApiResponse(success=True, data=result)
            else:
                return ApiResponse(
                    success=False,
                    error="Could not find valid JSON in the API response"
                )

        except json.JSONDecodeError as e:
            return ApiResponse(
                success=False,
                error=f"Failed to parse JSON: {str(e)}"
            )

    except Exception as e:
        return ApiResponse(
            success=False,
            error=f"Error generating topical map: {str(e)}"
        )


@app.post("/generate-meta-tags", response_model=ApiResponse)
async def generate_meta_tags(request: MetaTagsRequest) -> ApiResponse:
    try:
        # Replace placeholders in the prompt with user-provided values
        customized_prompt = (
            FRIENDLY_META_TAGS_PROMPT
            .replace("[primary_keyword]", request.primary_keyword)
            .replace("[secondary_keyword]", request.secondary_keyword)
            .replace("[brand_name]", request.brand_name)
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # You can change this to the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates SEO-friendly meta tags in the specified JSON format."},
                {"role": "user", "content": customized_prompt}
            ],
            temperature=0.7,
        )

        # Extract response content
        content = response.choices[0].message.content
        if content is None:
            return ApiResponse(
                success=False,
                error="No content returned from the API"
            )

        # Try to find and extract JSON from the response
        try:
            # Find JSON content (in case there's additional text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                json_data = json.loads(json_content)                # Validate that the required fields are present
                if "friendly_title" not in json_data or "meta_description" not in json_data:
                    return ApiResponse(
                        success=False,
                        error="API response is missing required fields"
                    )

                # Return the meta tags data
                return ApiResponse(success=True, data=json_data)
            else:
                return ApiResponse(
                    success=False,
                    error="Could not find valid JSON in the API response"
                )

        except json.JSONDecodeError as e:
            return ApiResponse(
                success=False,
                error=f"Failed to parse JSON: {str(e)}"
            )

    except Exception as e:
        return ApiResponse(
            success=False,
            error=f"Error generating meta tags: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
