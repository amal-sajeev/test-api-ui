from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import requests

@dataclass
class User:
    """Represents a user in the learning platform"""
    user_name: str
    client: str
    user_courses: List[str] = field(default_factory=list)
    user_modules: List[str] = field(default_factory=list)
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API submission"""
        return {
            "user_name": self.user_name,
            "client": self.client,
            "user_courses": self.user_courses,
            "user_modules": self.user_modules
        }

@dataclass
class Question:
    """Represents a question in the question bank"""
    question_content: str
    question_options: Dict[str, str]
    question_answer: str
    difficulty_rating: str
    question_subjects: List[str]
    course: str
    module: str
    _id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for API submission"""
        return {
            "question_content": self.question_content,
            "question_options": self.question_options,
            "question_answer": self.question_answer,
            "difficulty_rating": self.difficulty_rating,
            "question_subjects": self.question_subjects,
            "course": self.course,
            "module": self.module
        }

@dataclass
class Session:
    """Represents a learning session (assessment or practice)"""
    user: str
    client: str
    question_bank: str
    question_list: List[Dict[str, Any]]
    dynamic: bool = False
    max_score: int = 100
    _id: Optional[str] = None
    status: Optional[str] = None
    total_score: Optional[float] = None
    performance_score: Optional[float] = None

class LearningPlatformClient:
    """Main client for interacting with the learning platform API"""
    def __init__(self, base_url: str):
        """
        Initialize the client with the base URL of the API
        
        Args:
            base_url (str): Base URL of the API, e.g., 'http://localhost:8000'
        """
        self.base_url = base_url.rstrip('/')

    def create_client(self, client_name: str) -> str:
        """Create a new client database"""
        response = requests.post(f"{self.base_url}/clients/create", params={"client": client_name})
        response.raise_for_status()
        return response.json()

    def delete_client(self, client_uuid: str) -> None:
        """Delete a client database"""
        response = requests.post(f"{self.base_url}/{client_uuid}/delete")
        response.raise_for_status()

    def create_user(self, user: User) -> str:
        """
        Create a user in a specific client database
        
        Args:
            user (User): User object to create
        
        Returns:
            str: Created user's UUID
        """
        response = requests.post(f"{self.base_url}/{user.client}/users/create", json=user.to_dict())
        response.raise_for_status()
        user_id = response.json()['user_uuid']
        user.user_id = user_id
        return user_id

    def get_user(self, client: str, user_id: str) -> User:
        """Get user details"""
        response = requests.get(f"{self.base_url}/{client}/users/{user_id}")
        response.raise_for_status()
        user_data = response.json()
        return User(
            user_name=user_data.get('user_name', ''),
            client=client,
            user_courses=user_data.get('user_courses', []),
            user_modules=user_data.get('user_modules', []),
            user_id=user_id
        )

    def update_user(self, user: User) -> None:
        """Update user's courses and modules"""
        if not user.user_id:
            raise ValueError("User must have a user_id to update")
        
        data = {
            "courses": user.user_courses,
            "modules": user.user_modules
        }
        response = requests.put(f"{self.base_url}/{user.client}/users/{user.user_id}", json=data)
        response.raise_for_status()

    def delete_user(self, user: User) -> None:
        """Delete a user"""
        if not user.user_id:
            raise ValueError("User must have a user_id to delete")
        
        response = requests.delete(f"{self.base_url}/{user.client}/users/{user.user_id}")
        response.raise_for_status()

    def create_question_bank(self, client: str, bank_name: str) -> str:
        """Create a blank question bank"""
        response = requests.post(f"{self.base_url}/{client}/createbank", params={"bank": bank_name})
        response.raise_for_status()
        return response.json()

    def add_questions(self, client: str, bank: str, questions: List[Question]) -> List[str]:
        """Add questions to a bank"""
        question_dicts = [q.to_dict() for q in questions]
        response = requests.post(f"{self.base_url}/{client}/{bank}/add", json=question_dicts)
        response.raise_for_status()
        return response.json()

    def search_questions(self, client: str, bank: str, 
                         subjects: List[str] = None, 
                         difficulty: List[str] = None, 
                         course: List[str] = None, 
                         module: List[str] = None) -> List[Question]:
        """Search questions in a bank"""
        query = {k: v for k, v in locals().items() if v is not None and k not in ['self', 'client', 'bank']}
        response = requests.post(f"{self.base_url}/{client}/{bank}/search", json=query)
        response.raise_for_status()
        
        questions = []
        for q_data in response.json():
            question = Question(
                question_content=q_data['question_content'],
                question_options=q_data['question_options'],
                question_answer=q_data['question_answer'],
                difficulty_rating=q_data['difficulty_rating'],
                question_subjects=q_data['question_subjects'],
                course=q_data['course'],
                module=q_data['module'],
                _id=q_data.get('_id')
            )
            questions.append(question)
        
        return questions

    def create_assessment(self, session: Session) -> str:
        """Create an assessment"""
        response = requests.post(
            f"{self.base_url}/{session.client}/assessment/{session.user}/create", 
            json=session.__dict__
        )
        response.raise_for_status()
        session_id = response.json()
        session._id = session_id
        return session_id

    def start_assessment(self, session: Session, shuffle: bool = False) -> List[Dict[str, Any]]:
        """Start an assessment"""
        if not session._id:
            raise ValueError("Session must have an ID to start")
        
        response = requests.get(
            f"{self.base_url}/{session.client}/assessment/{session._id}/start", 
            params={"shuffle": shuffle}
        )
        response.raise_for_status()
        return response.json()

    def submit_assessment(self, session: Session) -> Dict[str, Any]:
        """Submit an assessment"""
        if not session._id:
            raise ValueError("Session must have an ID to submit")
        
        response = requests.post(
            f"{self.base_url}/{session.client}/assessment/{session._id}/submit", 
            json=session.__dict__
        )
        response.raise_for_status()
        return response.json()

class LearningPlatform:
    """Facade class to simplify interactions with the learning platform"""
    def __init__(self, base_url: str):
        """
        Initialize the learning platform
        
        Args:
            base_url (str): Base URL of the API
        """
        self.client = LearningPlatformClient(base_url)
        self.current_client: Optional[str] = None
        self.current_user: Optional[User] = None

    def setup_client(self, client_name: str) -> str:
        """
        Set up a new client and store its UUID
        
        Args:
            client_name (str): Name of the client to create
        
        Returns:
            str: Created client's UUID
        """
        self.current_client = self.client.create_client(client_name)
        return self.current_client

    def register_user(self, user_name: str, courses: List[str] = None, modules: List[str] = None) -> User:
        """
        Register a new user
        
        Args:
            user_name (str): Name of the user
            courses (List[str], optional): List of course IDs
            modules (List[str], optional): List of module IDs
        
        Returns:
            User: Created user object
        """
        if not self.current_client:
            raise ValueError("Must set up a client first")
        
        user = User(
            user_name=user_name,
            client=self.current_client,
            user_courses=courses or [],
            user_modules=modules or []
        )
        self.client.create_user(user)
        self.current_user = user
        return user

    def create_assessment_session(self, question_bank: str, dynamic: bool = False) -> Session:
        """
        Create an assessment session
        
        Args:
            question_bank (str): Name of the question bank to use
            dynamic (bool, optional): Whether to use dynamic assessment
        
        Returns:
            Session: Created assessment session
        """
        if not self.current_client or not self.current_user:
            raise ValueError("Must set up a client and user first")
        
        session = Session(
            user=self.current_user.user_id,
            client=self.current_client,
            question_bank=question_bank,
            question_list=[],
            dynamic=dynamic
        )
        self.client.create_assessment(session)
        return session