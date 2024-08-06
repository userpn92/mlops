from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import diskcache as dc
import logging
from prometheus_fastapi_instrumentator import Instrumentator

# Initialize FastAPI
app = FastAPI()

# Initialize diskcache
cache = dc.Cache('cache-directory')

# Load pre-trained models
fill_mask = pipeline("fill-mask", model="bert-base-uncased")
sentiment_analysis = pipeline("sentiment-analysis")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Prometheus Instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

class InputText(BaseModel):
    sentence: str

@app.post("/suggestions/", summary="Get Positive Suggestions for a Sentence",
          description="This endpoint accepts a sentence with a '<blank>' placeholder and returns a list of positive suggestions to fill in the blank.",
          response_model=dict)
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

    # Check if the response is cached
    cached_response = cache.get(input_text.sentence)
    if cached_response is not None:
        logger.info("Returning cached response")
        return {"suggestions": cached_response}

    # Generate suggestions
    suggestions = fill_mask(input_text.sentence.replace("<blank>", fill_mask.tokenizer.mask_token))

    # Filter suggestions based on sentiment
    positive_suggestions = []
    for suggestion in suggestions:
        sentiment = sentiment_analysis(suggestion['sequence'])
        if sentiment[0]['label'] == 'POSITIVE':
            positive_suggestions.append(suggestion['token_str'])

    # Cache the response
    cache.set(input_text.sentence, positive_suggestions)
    logger.info(f"Returning suggestions: {positive_suggestions}")
    return {"suggestions": positive_suggestions}
