# Ash Tech API

A FastAPI application that generates topical maps for SEO content strategies using OpenAI's API.

## Overview

This API allows users to generate comprehensive topical maps for SEO content planning. It takes a "money keyword" as input and returns a structured content plan with pillar pages, supporting pages, and blog topics.

## Features

- Generate topical maps using AI
- FastAPI backend for efficient API handling
- Comprehensive test suite

## Project Structure

- `main.py`: Core API implementation with FastAPI
- `datamodel.py`: Data models for the application
- `test_main.py`: Test suite for the API endpoints

## Getting Started

### Prerequisites

- Python 3.9+
- FastAPI
- OpenAI API key

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Running the API

```
uvicorn main:app --reload
```

### Running Tests

```
pytest
```

## License

[MIT License](LICENSE)