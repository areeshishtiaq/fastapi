"""
Prompt template definitions for the topical map generator.
"""

TOPICAL_MAP_PROMPT = """
Create a topical map for the keyword: [keyword]

The topical map should be structured as follows:
Stage 1: Main Topic
Stage 2: Pillar Pages (3-5 major content themes)
Stage 3: Supporting Content under each Pillar Page (2-3 items per pillar)
Stage 4: Blog Post Ideas under each Supporting Content (5-7 blog titles each)

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

FRIENDLY_META_TAGS_PROMPT = """
Create friendly SEO title and description with:
- Primary keyword: [primary_keyword]
- Secondary keyword: [secondary_keyword]
- Brand name: [brand_name]

Return the response in json format:
{
    "friendly_title": "string",
    "meta_description": "string",
}

Example:
Primary Keyword: Dentist in Northshore
Secondary Keyword: Dental Implant in Northshore
Brand Name: City Dentist

Result:
{
    "friendly_title": "Dentist in Northshore | Dental Implant Experts | City Dentist"
    "meta_description": "City Dentist – Looking for a trusted dentist in Northshore?
        We specialize in dental implants and personalized care to
        help you smile with confidence."
}
"""
