import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import rag
import db

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    conversation_id: str
    feedback: int


@app.post("/question")
async def handle_question(data: QuestionRequest):
    question = data.question

    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    conversation_id = str(uuid.uuid4())

    answer_data = rag(question)

    result = {
        "conversation_id": conversation_id,
        "question": question,
        "answer": answer_data["answer"],
    }

    db.save_conversation(
        conversation_id=conversation_id,
        question=question,
        answer_data=answer_data,
    )

    return result


@app.post("/feedback")
async def handle_feedback(data: FeedbackRequest):
    conversation_id = data.conversation_id
    feedback = data.feedback

    if not conversation_id or feedback not in [1, -1]:
        raise HTTPException(status_code=400, detail="Invalid input")

    db.save_feedback(
        conversation_id=conversation_id,
        feedback=feedback,
    )

    result = {
        "message": f"Feedback received for conversation {conversation_id}: {feedback}"
    }
    return result
