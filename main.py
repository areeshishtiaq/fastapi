import json
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from datamodel import TopicalMap, PillarPage

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Topical Map Generator API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
Create a topical map for the keyword: [keyword]

The topical map should be structured as follows:
Stage 1: Main Topic
Stage 2: Pillar Pages (3-5 major content themes)
Stage 3: Supporting Content under each Pillar Page (2-3 items per pillar)
Stage 4: Blog Post Ideas under each Supporting Content (2-3 blog titles each)

return the response in json format:
{
    "money_keyword": "string",
    "pillar_pages": [
        {
            "title": "string",
            "supporting_pages": ["string", ...],
            "supporting_blog_topics": ["string", ...]
        },
        ...
    ]
}
"""

class KeywordRequest(BaseModel):
    keyword: str

class TopicalMapResponse(BaseModel):
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
            supporting_blog_topics=pillar_page_data.get("supporting_blog_topics", [])
        )
        # Add to topical map
        topical_map.add_topic(pillar_page)
    
    return topical_map

@app.post("/generate-topical-map", response_model=TopicalMapResponse)
async def generate_topical_map(request: KeywordRequest) -> TopicalMapResponse:
    try:
        # Replace [keyword] in the prompt with the user-provided keyword
        customized_prompt = PROMPT.replace("[keyword]", request.keyword)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # You can change this to the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates topical maps in the specified JSON format."},
                {"role": "user", "content": customized_prompt}
            ],
            temperature=0.7,
        )
        
        # Extract response content
        content = response.choices[0].message.content
        
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
                        } for pillar in topical_map.pillar_pages
                    ]
                }
                
                return TopicalMapResponse(success=True, data=result)
            else:
                return TopicalMapResponse(
                    success=False,
                    error="Could not find valid JSON in the API response"
                )
                
        except json.JSONDecodeError as e:
            return TopicalMapResponse(
                success=False,
                error=f"Failed to parse JSON: {str(e)}"
            )
            
    except Exception as e:
        return TopicalMapResponse(
            success=False,
            error=f"Error generating topical map: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=443)


