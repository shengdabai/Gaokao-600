import base64
import binascii
from datetime import date, datetime
from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

Score150 = Annotated[float, Field(ge=0, le=150, allow_inf_nan=False)]
Score100 = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]
AIText = Annotated[str, Field(min_length=1, max_length=20000)]
AIContext = Annotated[str, Field(max_length=20000)]
Subject = Annotated[str, Field(max_length=50)]


# ── User ──────────────────────────────────────────────────────────────
class UserProfile(BaseModel):
    id: int
    name: str
    target_total_score: int
    target_chinese: int
    target_math: int
    target_english: int
    target_physics: int
    target_chemistry: int
    target_politics: int
    schedule_json: Optional[str] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    target_total_score: Optional[int] = Field(default=None, ge=0, le=750)
    target_chinese: Optional[int] = Field(default=None, ge=0, le=150)
    target_math: Optional[int] = Field(default=None, ge=0, le=150)
    target_english: Optional[int] = Field(default=None, ge=0, le=150)
    target_physics: Optional[int] = Field(default=None, ge=0, le=100)
    target_chemistry: Optional[int] = Field(default=None, ge=0, le=100)
    target_politics: Optional[int] = Field(default=None, ge=0, le=100)
    schedule_json: Optional[str] = None

    @field_validator("name", "target_total_score", "target_chinese", "target_math",
                     "target_english", "target_physics", "target_chemistry", "target_politics")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null; omit it to keep its current value")
        return value


# ── Exam ──────────────────────────────────────────────────────────────
class ExamCreate(BaseModel):
    exam_name: str
    exam_date: date
    chinese_score: Optional[Score150] = None
    math_score: Optional[Score150] = None
    english_score: Optional[Score150] = None
    physics_score: Optional[Score100] = None
    chemistry_score: Optional[Score100] = None
    politics_score: Optional[Score100] = None


class ExamOut(BaseModel):
    id: int
    user_id: int
    exam_name: str
    exam_date: date
    chinese_score: Optional[float] = None
    math_score: Optional[float] = None
    english_score: Optional[float] = None
    physics_score: Optional[float] = None
    chemistry_score: Optional[float] = None
    politics_score: Optional[float] = None
    total_score: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Diagnosis ─────────────────────────────────────────────────────────
class SubjectGap(BaseModel):
    subject: str
    subject_cn: str
    current: float
    target: int
    gap: float
    weighted_gap: float
    priority_rank: int


class DiagnosisResult(BaseModel):
    total_current: float
    total_target: int
    total_gap: float
    subject_gaps: List[SubjectGap]


# ── Plan ──────────────────────────────────────────────────────────────
class PlanGenerateRequest(BaseModel):
    start_date: Optional[date] = None  # defaults to today


class PlanOut(BaseModel):
    id: int
    user_id: int
    plan_type: str
    title: str
    content: Optional[str] = None
    start_date: date
    end_date: date
    status: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Task ──────────────────────────────────────────────────────────────
class TaskOut(BaseModel):
    id: int
    user_id: int
    subject: str
    title: str
    description: Optional[str] = None
    scheduled_date: date
    estimated_minutes: int
    completed: bool
    plan_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Wrong Question ───────────────────────────────────────────────────
class WrongQuestionCreate(BaseModel):
    subject: str
    question_text: str
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    error_reason: Optional[str] = None
    knowledge_point: Optional[str] = None


class WrongQuestionUpdate(BaseModel):
    mastery_status: Optional[Literal["not_mastered", "reviewing", "mastered"]] = None
    error_reason: Optional[str] = None
    knowledge_point: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None

    @field_validator("mastery_status")
    @classmethod
    def reject_null_status(cls, value):
        if value is None:
            raise ValueError("mastery_status cannot be null")
        return value


class WrongQuestionOut(BaseModel):
    id: int
    user_id: int
    subject: str
    question_text: str
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    error_reason: Optional[str] = None
    knowledge_point: Optional[str] = None
    mastery_status: str
    next_review_date: Optional[date] = None
    review_count: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── AI Review ────────────────────────────────────────────────────────
class ChineseReviewRequest(BaseModel):
    text: AIText


class PoliticsReviewRequest(BaseModel):
    question: AIText
    answer: AIText


class ImageInput(BaseModel):
    # At most 8 MiB decoded; reject malformed input before calling the paid API.
    base64_image: str = Field(min_length=1, max_length=11184812)

    @field_validator("base64_image")
    @classmethod
    def validate_image(cls, value: str) -> str:
        try:
            decoded = base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Invalid base64 image") from exc
        if len(decoded) > 8 * 1024 * 1024:
            raise ValueError("Image exceeds 8 MiB")
        return value


class ImageAnalyzeRequest(ImageInput):
    subject: Subject = "general"


class SearchNotesRequest(BaseModel):
    query: AIText
    subject: Subject = "general"


class AIReviewResponse(BaseModel):
    feedback: str


class RecognizeQuestionRequest(ImageInput):
    subject: Optional[Subject] = None


class RecognizeQuestionResponse(BaseModel):
    subject: str
    question_text: str
    user_answer: str
    correct_answer: str
    error_reason: str
    knowledge_point: str


class SimilarQuestionsRequest(BaseModel):
    question_text: AIText
    subject: Subject
    knowledge_point: AIContext
    error_reason: AIContext


class CheckAnswerRequest(BaseModel):
    question: AIText
    subject: Subject
    user_answer: AIText


class EnglishReviewRequest(BaseModel):
    text: AIText


# ── Weekly Review ────────────────────────────────────────────────────
class WeeklyReviewOut(BaseModel):
    week_start: date
    week_end: date
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    wrong_questions_reviewed: int
    wrong_questions_mastered: int
    subject_breakdown: Dict[str, Any]
    suggestions: List[str]
    ai_summary: Optional[str] = None
