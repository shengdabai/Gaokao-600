from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import DEFAULT_USER_ID
from app.database import get_db
from app.models.models import MasteryStatus, WrongQuestion
from app.schemas.schemas import WrongQuestionCreate, WrongQuestionOut, WrongQuestionUpdate
from app.services.wrong_question_scheduler import WrongQuestionScheduler

router = APIRouter(prefix="/api/wrong-questions", tags=["wrong_question"])

USER_ID = DEFAULT_USER_ID


@router.post("", response_model=WrongQuestionOut)
def create_wrong_question(payload: WrongQuestionCreate, db: Session = Depends(get_db)):
    wq = WrongQuestion(
        user_id=USER_ID,
        subject=payload.subject,
        question_text=payload.question_text,
        user_answer=payload.user_answer,
        correct_answer=payload.correct_answer,
        error_reason=payload.error_reason,
        knowledge_point=payload.knowledge_point,
    )
    scheduler = WrongQuestionScheduler(db)
    wq = scheduler.schedule_new_question(wq)
    db.add(wq)
    db.commit()
    db.refresh(wq)
    return wq


@router.get("", response_model=List[WrongQuestionOut])
def list_wrong_questions(
    subject: Optional[str] = None,
    status: Optional[MasteryStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(WrongQuestion).filter(WrongQuestion.user_id == USER_ID)
    if subject:
        query = query.filter(WrongQuestion.subject == subject)
    if status:
        query = query.filter(WrongQuestion.mastery_status == status)
    return query.order_by(WrongQuestion.created_at.desc()).all()


@router.put("/{wq_id}", response_model=WrongQuestionOut)
def update_wrong_question(
    wq_id: int, payload: WrongQuestionUpdate, db: Session = Depends(get_db)
):
    wq = (
        db.query(WrongQuestion)
        .filter(WrongQuestion.id == wq_id, WrongQuestion.user_id == USER_ID)
        .first()
    )
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")

    update_data = payload.model_dump(exclude_unset=True)

    if "mastery_status" in update_data:
        new_status = update_data.pop("mastery_status")
        scheduler = WrongQuestionScheduler(db)
        if new_status == MasteryStatus.mastered.value:
            scheduler.mark_reviewed(wq, mastered=True)
        elif new_status == MasteryStatus.not_mastered.value:
            scheduler.mark_reviewed(wq, mastered=False)
        elif new_status == MasteryStatus.reviewing.value:
            wq.mastery_status = MasteryStatus.reviewing

    for key, value in update_data.items():
        setattr(wq, key, value)

    db.commit()
    db.refresh(wq)
    return wq


@router.delete("/{wq_id}")
def delete_wrong_question(wq_id: int, db: Session = Depends(get_db)):
    wq = (
        db.query(WrongQuestion)
        .filter(WrongQuestion.id == wq_id, WrongQuestion.user_id == USER_ID)
        .first()
    )
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(wq)
    db.commit()
    return {"detail": "删除成功"}
