from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from transformers import pipeline
import diskcache as dc
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables for models and cache
fill_mask = None
sentiment_analysis = None
cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global fill_mask, sentiment_analysis, cache

    # Load configuration
    fill_mask_model = os.getenv("FILL_MASK_MODEL", "bert-base-uncased")
    sentiment_model = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
    cache_dir = os.getenv("CACHE_DIR", "cache-directory")

    logger.info(f"Loading models: {fill_mask_model}, {sentiment_model}")

    try:
        # Load models
        fill_mask = pipeline("fill-mask", model=fill_mask_model)
        sentiment_analysis = pipeline("sentiment-analysis", model=sentiment_model)

        # Initialize cache
        cache = dc.Cache(cache_dir)
        logger.info("Models and cache loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise e

    yield

    # Clean up
    if cache:
        cache.close()
    logger.info("Shutting down")

# Initialize FastAPI
app = FastAPI(lifespan=lifespan)

# Initialize Prometheus Instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

class InputText(BaseModel):
    sentence: str

class SuggestionResponse(BaseModel):
    suggestions: list[str]

@app.get("/health", summary="Health Check", description="Returns the status of the application.")
async def health_check():
    return {"status": "ok"}

def filter_positive_suggestions(suggestions):
    """
    Helper function to filter suggestions based on sentiment.
    This function is CPU-bound and should be run in a threadpool.
    """
    positive_suggestions = []
    for suggestion in suggestions:
        try:
            sentiment = sentiment_analysis(suggestion['sequence'])
            if sentiment[0]['label'] == 'POSITIVE':
                positive_suggestions.append(suggestion['token_str'])
        except Exception as e:
            logger.warning(f"Error analyzing sentiment for suggestion {suggestion}: {e}")
            continue
    return positive_suggestions

@app.post("/suggestions/", summary="Get Positive Suggestions for a Sentence",
          description="This endpoint accepts a sentence with a '<blank>' placeholder and returns a list of positive suggestions to fill in the blank.",
          response_model=SuggestionResponse)
async def get_suggestions(input_text: InputText):
    """
    Get suggestions for filling in the blank in a sentence.

    - **sentence**: The input sentence containing a '<blank>' placeholder.
    """
    logger.info(f"Received input: {input_text.sentence}")

    # Validate input
    if "<blank>" not in input_text.sentence:
        logger.error("Input validation failed: '<blank>' not found")
        raise HTTPException(status_code=400, detail="Input must contain '<blank>'")

    # Check if models are loaded
    if fill_mask is None or sentiment_analysis is None or cache is None:
        logger.error("Models not loaded")
        raise HTTPException(status_code=503, detail="Service unavailable: Models not loaded")

    # Check if the response is cached
    cached_response = cache.get(input_text.sentence)
    if cached_response is not None:
        logger.info("Returning cached response")
        return {"suggestions": cached_response}

    # Generate suggestions
    try:
        masked_input = input_text.sentence.replace("<blank>", fill_mask.tokenizer.mask_token)
        suggestions = await run_in_threadpool(fill_mask, masked_input)
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")

    # Filter suggestions based on sentiment
    try:
        positive_suggestions = await run_in_threadpool(filter_positive_suggestions, suggestions)
    except Exception as e:
        logger.error(f"Error filtering suggestions: {e}")
        raise HTTPException(status_code=500, detail="Error processing suggestions")

    # Cache the response
    cache.set(input_text.sentence, positive_suggestions)
    logger.info(f"Returning suggestions: {positive_suggestions}")
    return {"suggestions": positive_suggestions}
