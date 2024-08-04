from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# Initialize FastAPI
app = FastAPI()

## Load pre-trained models
fill_mask = pipeline("fill-mask", model="bert-base-uncased")
sentiment_analysis = pipeline("sentiment-analysis")

class InputText(BaseModel):
    sentence: str

@app.post("/suggestions/")
async def get_suggestions(input_text: InputText):
    # Validate input
    if "<blank>" not in input_text.sentence:
        raise HTTPException(status_code=400, detail="Input must contain '<blank>'")

    # Generate suggestions
    suggestions = fill_mask(input_text.sentence.replace("<blank>", fill_mask.tokenizer.mask_token))
    
    # Filter suggestions based on sentiment
    positive_suggestions = []
    for suggestion in suggestions:
        sentiment = sentiment_analysis(suggestion['sequence'])
        if sentiment[0]['label'] == 'POSITIVE':
            positive_suggestions.append(suggestion['token_str'])

    return {"suggestions": positive_suggestions}

