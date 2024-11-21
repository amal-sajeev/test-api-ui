import requests
from typing import List, Dict, Optional, Union
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserCreate:
    user_name: str
    client: str
    user_courses: List[str]
    user_modules: List[str]

@dataclass
class UserUpdate:
    courses: List[str]
    modules: List[str]

@dataclass
class QuestionQuery:
    course: List[str]
    subjects: Optional[List[str]] = None
    difficulty: Optional[List[int]] = None
    module: Optional[List[str]] = None

@dataclass
class Question:
    question_content: str
    question_options: Dict[str, str]
    question_answer: str
    difficulty_rating: Union[str, int]
    question_subjects: List[str]
    course: str
    module: str
    client: str

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8100"):
        """Initialize the API client.
        
        Args:
            base_url: The base URL of the API server
        """
        self.base_url = base_url.rstrip('/')

    # User Management
    def create_user(self, user: UserCreate) -> str:
        """Create a new user."""
        response = requests.post(
            f"{self.base_url}/{user.client}/users/create",
            json=user.__dict__
        )
        response.raise_for_status()
        return response.json()["user_uuid"]

    def get_user(self, client: str, user_id: str) -> dict:
        """Get user details."""
        response = requests.get(
            f"{self.base_url}/{client}/users/{user_id}"
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, client: str, user_id: str, update: UserUpdate) -> None:
        """Update user details."""
        response = requests.put(
            f"{self.base_url}/{client}/users/{user_id}",
            json=update.__dict__
        )
        response.raise_for_status()

    def get_upcoming(self, client:str, user_id:str):
        """Get upcoming cards for the user"""
        response = requests.get(
            f"{self.base_url}/{client}/users/{user_id}/upcoming"
        )
        response.raise_for_status()
        return response.json()

    def delete_user(self, client: str, user_id: str) -> None:
        """Delete a user."""
        response = requests.delete(
            f"{self.base_url}/{client}/users/{user_id}"
        )
        response.raise_for_status()

    # Question Bank Management
    def create_bank(self, client: str, bank: str) -> dict:
        """Create a new question bank."""
        response = requests.post(
            f"{self.base_url}/{client}/createbank",
            params={"bank": bank}
        )
        response.raise_for_status()
        return response.json()
    
    def get_bank(self, client: str, bank: str) -> List[dict]:
        """Get all questions from a bank."""
        response = requests.get(
            f"{self.base_url}/{client}/{bank}/"
        )
        response.raise_for_status()
        return response.json()

    def get_all_banks(self, client:str):
        """Get all question banks in a client's database"""
        response = requests.get(
            f"{self.base_url}/{client}/banks"
        )
        response.raise_for_status()
        return response.json()

    def add_questions(self, client: str, bank: str, questions: List[Question]) -> dict:
        """Add questions to a bank."""
        response = requests.post(
            f"{self.base_url}/{client}/{bank}/add",
            json=[q.__dict__ for q in questions]
        )
        response.raise_for_status()
        return response.json()

    def upload_question_bank(self, client: str, bank: str, file_path: str) -> str:
        """Upload an Excel/CSV file of questions."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/{client}/{bank}/upload",
                files=files
            )
        response.raise_for_status()
        return response.json()

    def search_questions(self, client: str, bank: str, query: QuestionQuery) -> List[dict]:
        """Search for questions using various criteria."""
        response = requests.post(
            f"{self.base_url}/{client}/{bank}/search",
            json=query.__dict__
        )
        response.raise_for_status()
        return response.json()

    def get_questions(self, client: str, bank: str, question_ids: List[str]) -> List[dict]:
        """Get specific questions by their IDs."""
        response = requests.post(
            f"{self.base_url}/{client}/{bank}/get",
            json=question_ids
        )
        response.raise_for_status()
        return response.json()

    def update_questions(self, client: str, bank: str, questions: List[Question]) -> dict:
        """Update existing questions."""
        response = requests.put(
            f"{self.base_url}/{client}/{bank}/update",
            json=[q.__dict__ for q in questions]
        )
        response.raise_for_status()
        return response.json()

    def delete_questions(self, client: str, bank: str, question_ids: List[str]) -> dict:
        """Delete questions from a bank."""
        response = requests.delete(
            f"{self.base_url}/{client}/{bank}/delete",
            json=question_ids
        )
        response.raise_for_status()
        return response.json()

    # Assessment Management
    def create_assessment(self, client: str, user_id: str, session_data: dict) -> str:
        """Create a new assessment session."""
        response = requests.post(
            f"{self.base_url}/{client}/assessment/{user_id}/create",
            json=session_data
        )
        response.raise_for_status()
        return response.json()

    def start_assessment(self, client: str, session_id: str) -> List[dict]:
        """Start an assessment session."""
        response = requests.get(
            f"{self.base_url}/{client}/assessment/{session_id}/start"
        )
        response.raise_for_status()
        return response.json()

    def submit_assessment(self, client: str, session_id: str, session_data: dict) -> dict:
        """Submit an assessment session."""
        response = requests.post(
            f"{self.base_url}/{client}/assessment/{session_id}/submit",
            json=session_data
        )
        response.raise_for_status()
        return response.json()

    # Practice Management
    def create_practice(self, client: str, user_id: str, session_data: dict) -> str:
        """Create a new practice session."""
        response = requests.post(
            f"{self.base_url}/{client}/practice/{user_id}/create",
            json=session_data
        )
        response.raise_for_status()
        return response.json()

    def start_practice(self, client: str, session_id: str) -> dict:
        """Start a practice session."""
        response = requests.get(
            f"{self.base_url}/{client}/practice/{session_id}/start"
        )
        response.raise_for_status()
        return response.json()

    def continue_practice(self, client: str, session_id: str, answer_selection: str, answer_difficulty_selection: int) -> dict:
        """Continue a practice session with next question."""
        response = requests.post(
            f"{self.base_url}/{client}/practice/{session_id}/next",
            json={
                "answer_selection": answer_selection,
                "answer_difficulty_selection": answer_difficulty_selection
            }
        )
        response.raise_for_status()
        return response.json()