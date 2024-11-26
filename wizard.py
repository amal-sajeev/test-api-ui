import requests
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

class APIException(Exception):
    """Custom exception for API-related errors"""
    pass

@dataclass
class User:
    user_name: str
    client: str
    user_courses: List[str]
    user_modules: List[str]

@dataclass
class QuestionQuery:
    subjects: Optional[List[str]] = None
    difficulty: Optional[List[str]] = None
    course: List[str] = None
    module: Optional[List[str]] = None

@dataclass
class Question:
    question_content: str
    question_options: Dict[str, str]
    question_answer: str
    difficulty_rating: str
    question_subjects: List[str]
    course: str
    module: str

@dataclass
class Session:
    user: str
    bank: str
    client: str
    dynamic: bool = False
    max_score: float = 100.0
    question_list: List[Dict] = None

@dataclass
class DynoEntry:
    """
    Entry for dynamic assessment next endpoint
    """
    question_id: str
    answer_selection: str

@dataclass
class NextEntry:
    """
    Entry for practice session next endpoint
    """
    answer_selection: str
    answer_difficulty_selection: int

class LearningPlatformClient:
    def __init__(self, base_url: str):
        """
        Initialize the client with the base URL of the API
        
        Args:
            base_url (str): Base URL of the API (e.g., 'http://localhost:8000')
        """
        self.base_url = base_url.rstrip('/')

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None):
        """
        Helper method to make HTTP requests with error handling
        
        Args:
            method (str): HTTP method (get, post, put, delete)
            endpoint (str): API endpoint
            data (Dict, optional): Request payload
            params (Dict, optional): Query parameters
        
        Returns:
            Response from the API
        
        Raises:
            APIException: For any API-related errors
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIException(f"API Request Failed: {str(e)}")

    # USER MANAGEMENT METHODS
    def create_user(self, client: str, user: User) -> str:
        """
        Create a new user
        
        Args:
            client (str): Client database
            user (User): User details
        
        Returns:
            str: User UUID
        """
        endpoint = f"{client}/users/create"
        response = self._make_request('post', endpoint, data=asdict(user))
        return response.get('user_uuid')

    def get_user(self, client: str, user_id: str) -> Dict:
        """
        Retrieve user details
        
        Args:
            client (str): Client database
            user_id (str): User UUID
        
        Returns:
            Dict: User details
        """
        endpoint = f"{client}/users/{user_id}"
        return self._make_request('get', endpoint)

    def update_user(self, client: str, user_id: str, courses: List[str], modules: List[str]):
        """
        Update user's courses and modules
        
        Args:
            client (str): Client database
            user_id (str): User UUID
            courses (List[str]): List of course IDs
            modules (List[str]): List of module IDs
        """
        endpoint = f"{client}/users/{user_id}"
        data = {"courses": courses, "modules": modules}
        self._make_request('put', endpoint, data=data)

    def delete_user(self, client: str, user_id: str):
        """
        Delete a user
        
        Args:
            client (str): Client database
            user_id (str): User UUID
        """
        endpoint = f"{client}/users/{user_id}"
        self._make_request('delete', endpoint)

    # NEW USER SESSION METHODS
    def get_user_assessments(self, client: str, user_id: str) -> List[Dict]:
        """
        Retrieve all assessments for a user
        
        Args:
            client (str): Client database
            user_id (str): User UUID
        
        Returns:
            List of assessment sessions
        """
        endpoint = f"{client}/users/{user_id}/assessments"
        return self._make_request('get', endpoint)

    def get_user_practice_sessions(self, client: str, user_id: str) -> List[Dict]:
        """
        Retrieve all practice sessions for a user
        
        Args:
            client (str): Client database
            user_id (str): User UUID
        
        Returns:
            List of practice sessions
        """
        endpoint = f"{client}/users/{user_id}/practice"
        return self._make_request('get', endpoint)

    def get_user_all_sessions(self, client: str, user_id: str) -> List[Dict]:
        """
        Retrieve all sessions (assessments and practice) for a user
        
        Args:
            client (str): Client database
            user_id (str): User UUID
        
        Returns:
            List of all sessions
        """
        endpoint = f"{client}/users/{user_id}/sessions"
        return self._make_request('get', endpoint)

    # QUESTION BANK METHODS
    def create_question_bank(self, client: str, bank: str):
        """
        Create a new question bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
        """
        endpoint = f"{client}/createbank"
        self._make_request('post', endpoint, params={'bank': bank})

    def get_all_banks(self, client: str) -> List[str]:
        """
        Retrieve all question banks for a client
        
        Args:
            client (str): Client database
        
        Returns:
            List[str]: Bank names
        """
        endpoint = f"{client}/banks"
        return self._make_request('get', endpoint)

    def get_bank_questions(self, client: str, bank: str) -> List[Question]:
        """
        Retrieve all questions in a bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
        
        Returns:
            List[Question]: Questions in the bank
        """
        endpoint = f"{client}/{bank}"
        return self._make_request('get', endpoint)

    def add_questions_to_bank(self, client: str, bank: str, questions: List[Question]):
        """
        Add questions to a bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
            questions (List[Question]): Questions to add
        """
        endpoint = f"{client}/{bank}/add"
        self._make_request('post', endpoint, data=questions)

    def search_questions(self, client: str, bank: str, query: QuestionQuery) -> List[Question]:
        """
        Search questions in a bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
            query (QuestionQuery): Search parameters
        
        Returns:
            List[Question]: Matching questions
        """
        endpoint = f"{client}/{bank}/search"
        return self._make_request('post', endpoint, data=asdict(query))

    # ENHANCED QUESTION BANK METHODS
    def rename_bank(self, client: str, bank: str, new_name: str):
        """
        Rename an existing question bank
        
        Args:
            client (str): Client database
            bank (str): Current bank name
            new_name (str): New bank name
        """
        endpoint = f"{client}/{bank}"
        self._make_request('put', endpoint, params={'newname': new_name})

    def upload_bank(self, client: str, bank: str, file_path: str):
        """
        Upload an Excel or CSV file to create a question bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
            file_path (str): Path to the Excel or CSV file
        """
        endpoint = f"{client}/{bank}/upload"
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(
                f"{self.base_url}/{endpoint}", 
                files=files
            )
        
        if response.status_code != 201:
            raise APIException(f"File upload failed: {response.text}")
        
        return response.json()

    def move_questions(self, client: str, bank: str, question_ids: List[str], new_bank: str):
        """
        Move questions from one bank to another
        
        Args:
            client (str): Client database
            bank (str): Source bank name
            question_ids (List[str]): IDs of questions to move
            new_bank (str): Destination bank name
        """
        endpoint = f"{client}/{bank}/move"
        self._make_request('put', endpoint, data={
            'question_ids': question_ids,
            'new_bank': new_bank
        })

    def update_questions(self, client: str, bank: str, questions: List[Question]):
        """
        Update existing questions in a bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
            questions (List[Question]): Updated questions
        """
        endpoint = f"{client}/{bank}/update"
        self._make_request('put', endpoint, data=[asdict(q) for q in questions])

    def get_specific_questions(self, client: str, bank: str, question_ids: List[str]) -> List[Question]:
        """
        Retrieve specific questions by their IDs
        
        Args:
            client (str): Client database
            bank (str): Bank name
            question_ids (List[str]): Question IDs to retrieve
        
        Returns:
            List of matching questions
        """
        endpoint = f"{client}/{bank}/get"
        return self._make_request('post', endpoint, data=question_ids)

    def delete_questions(self, client: str, bank: str, question_ids: List[str]):
        """
        Delete specific questions from a bank
        
        Args:
            client (str): Client database
            bank (str): Bank name
            question_ids (List[str]): Question IDs to delete
        """
        endpoint = f"{client}/{bank}/delete"
        self._make_request('delete', endpoint, data=question_ids)

    # ASSESSMENT METHODS
    def create_assessment(self, client: str, user_id: str, session: Session):
        """
        Create an assessment session
        
        Args:
            client (str): Client database
            user_id (str): User UUID
            session (Session): Session details
        
        Returns:
            Session details
        """
        endpoint = f"{client}/assessment/{user_id}/create"
        return self._make_request('post', endpoint, data=asdict(session))

    def start_assessment(self, client: str, session_id: str, shuffle: bool = True):
        """
        Start an assessment
        
        Args:
            client (str): Client database
            session_id (str): Session ID
            shuffle (bool, optional): Shuffle questions. Defaults to True.
        
        Returns:
            First question or full question list
        """
        endpoint = f"{client}/assessment/{session_id}/start"
        return self._make_request('get', endpoint, params={'shuffle': shuffle})

    def submit_assessment(self, client: str, session_id: str, session: Session):
        """
        Submit an assessment
        
        Args:
            client (str): Client database
            session_id (str): Session ID
            session (Session): Completed session details
        
        Returns:
            Assessment results
        """
        endpoint = f"{client}/assessment/{session_id}/submit"
        return self._make_request('post', endpoint, data=asdict(session))

    def assessment_next(self, client: str, session_id: str, entry: DynoEntry) -> Dict:
        """
        Proceed to the next question in a dynamic assessment
        
        Args:
            client (str): Client database
            session_id (str): Session ID
            entry (DynoEntry): Question response details
        
        Returns:
            Dict: Next question or assessment completion details
        """
        endpoint = f"{client}/assessment/{session_id}/next"
        return self._make_request('post', endpoint, data=asdict(entry))

    # PRACTICE METHODS
    def create_practice_session(self, client: str, user_id: str, session: Session):
        """
        Create a practice session
        
        Args:
            client (str): Client database
            user_id (str): User UUID
            session (Session): Session details
        
        Returns:
            Session details
        """
        endpoint = f"{client}/practice/{user_id}/create"
        return self._make_request('post', endpoint, data=asdict(session))

    def start_practice(self, client: str, session_id: str):
        """
        Start a practice session
        
        Args:
            client (str): Client database
            session_id (str): Session ID
        
        Returns:
            First practice question
        """
        endpoint = f"{client}/practice/{session_id}/start"
        return self._make_request('get', endpoint)

    def practice_next(self, client: str, session_id: str, entry: NextEntry) -> Dict:
        """
        Proceed to the next question in a practice session
        
        Args:
            client (str): Client database
            session_id (str): Session ID
            entry (NextEntry): Question response details
        
        Returns:
            Dict: Next question in the practice session
        """
        endpoint = f"{client}/practice/{session_id}/next"
        return self._make_request('post', endpoint, data=asdict(entry))

# Example Usage
def main():
    client = LearningPlatformClient('http://localhost:8100')
    
    # Create a new user
    new_user = User(
        user_name='john_doe', 
        client='myclient', 
        user_courses=['course1', 'course2'], 
        user_modules=['module1']
    )
    user_id = client.create_user('myclient', new_user)
    
    # Create a practice session
    practice_session = Session(
        user=user_id,
        bank='math_bank',
        client='myclient',
        dynamic=True
    )
    created_practice_session = client.create_practice_session('myclient', user_id, practice_session)
    
    # Start the practice session
    first_practice_question = client.start_practice('myclient', created_practice_session['session_id'])
    
    # Simulate responding to a practice question
    practice_response = NextEntry(
        answer_selection='b',
        answer_difficulty_selection=2
    )
    print(client.practice_next('myclient', created_practice_session['session_id'], practice_response))

if __name__ == "__main__":
    main()