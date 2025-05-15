from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import requests
from io import StringIO
import random

app = FastAPI()

# ✅ CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://betamathfrontend.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Google Sheet CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT42w5Uhe0AhKU-bfsOHFdRNW3YjhbmYlq_KfREwKxnV4kGEqRN9DhGGICZttLs-9hykPC9thnkhGzQ/pub?output=csv"

def fetch_questions_from_sheet():
    response = requests.get(CSV_URL)
    f = StringIO(response.text)
    reader = csv.DictReader(f)
    return list(reader)

# ✅ GET /questions with optional topic filtering
@app.get("/questions")
def get_questions(request: Request):
    topic_query = request.query_params.get("topics")
    all_questions = fetch_questions_from_sheet()

    if topic_query:
        selected_topics = [t.strip().lower() for t in topic_query.split(",")]
        filtered_questions = [
            q for q in all_questions if q["topic"].strip().lower() in selected_topics
        ]
    else:
        filtered_questions = all_questions

    random.shuffle(filtered_questions)
    return filtered_questions

# ✅ POST /submit to check student's answer
@app.post("/submit")
async def submit_answer(request: Request):
    data = await request.json()
    question_id = data.get("question_id")
    student_answer = data.get("answer")

    question_bank = fetch_questions_from_sheet()
    question = next((q for q in question_bank if q["id"] == str(question_id)), None)

    if not question:
        return JSONResponse(status_code=404, content={"error": "Question not found"})

    is_correct = student_answer.strip() == question["answer"].strip()
    return {
        "correct": is_correct,
        "explanation": question.get("explanation") if is_correct else None
    }
