from fastapi import FastAPI
from pydantic import BaseModel  # Import BaseModel from Pydantic
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from mangum import Mangum


device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

app = FastAPI()
# handler = Mangum(app)

class InputData(BaseModel):
    input: str

def estimate_sentiment(input: str):
    if input:
        tokens = tokenizer(input, return_tensors="pt", padding=True).to(device)
        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
        result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
        probability = result[torch.argmax(result)]
        sentiment = labels[torch.argmax(result)]

        # used to decode the tokenized test dont really ned it but its there
        # decoded_text = tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        # return probability.item(), sentiment, decoded_text

        return probability.item(), sentiment
    else:
        return 0, labels[-1]

@app.post("/analyze")
def analyze(data: InputData):
    probability, sentiment = estimate_sentiment(data.input)
    return {"probability": probability, "sentiment": sentiment}


# Run the app locally with Uvicorn
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
