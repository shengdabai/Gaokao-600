import base64
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import User
from app.routes import user as user_routes


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)

        def database():
            with self.sessions() as session:
                yield session

        app.dependency_overrides[get_db] = database
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_configured_profile_is_used_for_reads_and_updates(self):
        with patch.object(user_routes, "DEFAULT_USER_ID", 7, create=True):
            self.assertEqual(self.client.get("/api/user/profile").json()["id"], 7)
            response = self.client.put("/api/user/profile", json={"name": "student"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["id"], 7)
        with self.sessions() as session:
            self.assertIsNone(session.get(User, 1))

    def test_daily_task_dates_are_validated(self):
        self.assertEqual(self.client.get("/api/tasks/daily").status_code, 200)
        self.assertEqual(
            self.client.get("/api/tasks/daily", params={"date": date.today().isoformat()}).status_code,
            200,
        )
        for value in ["bad", "2026-02-30", ""]:
            with self.subTest(value=value):
                self.assertEqual(
                    self.client.get("/api/tasks/daily", params={"date": value}).status_code, 422
                )

    def test_wrong_question_states_are_validated_without_mutation(self):
        created = self.client.post(
            "/api/wrong-questions", json={"subject": "math", "question_text": "1+1?"}
        )
        self.assertEqual(created.status_code, 200)
        question_id = created.json()["id"]
        self.assertEqual(
            self.client.get("/api/wrong-questions?status=not_mastered").status_code, 200
        )
        self.assertEqual(self.client.get("/api/wrong-questions?status=bad").status_code, 422)
        for value in ["bad", None]:
            self.assertEqual(
                self.client.put(
                    f"/api/wrong-questions/{question_id}", json={"mastery_status": value}
                ).status_code,
                422,
            )
        self.assertEqual(self.client.get("/api/wrong-questions").json()[0]["review_count"], 0)
        self.assertEqual(
            self.client.put(
                f"/api/wrong-questions/{question_id}", json={"mastery_status": "mastered"}
            ).status_code,
            200,
        )

    def test_scores_are_finite_and_within_subject_limits(self):
        payload = {"exam_name": "mock", "exam_date": "2026-11-10"}
        for field, value in [("math_score", -1), ("math_score", 151),
                             ("physics_score", 101), ("chinese_score", "NaN"),
                             ("english_score", "Infinity")]:
            with self.subTest(field=field, value=value):
                self.assertEqual(
                    self.client.post("/api/exams", json={**payload, field: value}).status_code, 422
                )
        self.assertEqual(self.client.post("/api/exams", json={**payload, "math_score": 150}).status_code, 200)

    def test_profile_rejects_null_or_invalid_targets(self):
        for data in [{"name": None}, {"target_total_score": None}, {"target_math": -1},
                     {"target_total_score": 751}]:
            self.assertEqual(self.client.put("/api/user/profile", json=data).status_code, 422)
        self.assertEqual(self.client.put("/api/user/profile", json={}).status_code, 200)
        self.assertEqual(self.client.put("/api/user/profile", json={"schedule_json": None}).status_code, 200)

    def test_image_validation_prevents_upstream_calls(self):
        with patch("app.services.ai_service._get_client") as upstream:
            for endpoint in ["analyze-image", "recognize-question"]:
                for image in ["", "%%%", "YWJj$", "a" * 11184813]:
                    response = self.client.post(f"/api/ai/{endpoint}", json={"base64_image": image})
                    self.assertEqual(response.status_code, 422)
            upstream.assert_not_called()

    def test_ai_recognition_validates_untrusted_model_output(self):
        image = base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()
        valid = '{"subject":"math","question_text":"1+1?","user_answer":"3",' \
                '"correct_answer":"2","error_reason":"addition","knowledge_point":"arithmetic"}'
        for output in [None, "```", "not JSON", "[]", "null", "{}", '{"subject":1}',
                       '{"error":{"private":"upstream details"}}', valid, f"```json\n{valid}\n```"]:
            with self.subTest(output=output):
                upstream = SimpleNamespace(models=SimpleNamespace(
                    generate_content=lambda **kwargs: SimpleNamespace(text=output)
                ))
                with patch("app.services.ai_service._get_client", return_value=upstream):
                    response = self.client.post("/api/ai/recognize-question", json={"base64_image": image})
                self.assertEqual(response.status_code, 200 if output in [valid, f"```json\n{valid}\n```"] else 422)
                self.assertNotIn("upstream details", response.text)

    def test_ai_text_limits_prevent_upstream_calls(self):
        cases = [
            ("chinese-review", {"text": ""}),
            ("english-review", {"text": "a" * 20001}),
            ("politics-review", {"question": "?", "answer": "a" * 20001}),
            ("search-notes", {"query": "?", "subject": "a" * 51}),
            ("check-answer", {"question": "?", "subject": "math", "user_answer": ""}),
            ("similar-questions", {"question_text": "?", "subject": "math",
                                   "knowledge_point": "a" * 20001, "error_reason": ""}),
        ]
        with patch("app.services.ai_service._get_client") as upstream:
            for endpoint, payload in cases:
                with self.subTest(endpoint=endpoint):
                    self.assertEqual(self.client.post(f"/api/ai/{endpoint}", json=payload).status_code, 422)
            upstream.assert_not_called()


if __name__ == "__main__":
    unittest.main()
