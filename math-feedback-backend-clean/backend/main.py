from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load questions
with open("data/questions.json") as f:
    question_bank = json.load(f)

@app.get("/questions")
def get_questions():
    return question_bank

@app.post("/submit")
async def submit_answer(request: Request):
    data = await request.json()
    question_id = data.get("question_id")
    student_answer = data.get("answer")

    question = next((q for q in question_bank if q["id"] == question_id), None)
    if not question:
        return JSONResponse(status_code=404, content={"error": "Question not found"})

    is_correct = student_answer.strip() == question["answer"].strip()
    return {
        "correct": is_correct,
        "explanation": question["explanation"] if is_correct else None
    }
