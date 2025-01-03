import requests
from typing import List, Dict, Any, Union, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import pprint
import json
import streamlit as st

class APIClient:
    def __init__(self, base_url: str):
        """Base API client with common request handling and logging"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _log_request(self, method: str, full_url: str, **kwargs):
        """Log request details to request.txt"""
        
        with open('prequest.txt' if method != "GET" else 'grequest.txt' , 'w') as f:
            f.write(f"Method: {method}\n")
            f.write(f"URL: {full_url}\n")
            
            # Log parameters
            if 'params' in kwargs:
                f.write("Parameters:\n")
                f.write(json.dumps(kwargs['params'], indent=2) + "\n")
            
            # Log JSON payload
            if 'json' in kwargs:
                f.write("JSON Payload:\n")
                f.write(json.dumps(kwargs['json'], indent=2) + "\n")
            
            # Log files if present
            if 'files' in kwargs:
                f.write("Files:\n")
                f.write(str(kwargs['files']) + "\n")

    def _log_response(self, method, response):
        """Log response details to response.txt"""
        with open('presponse.txt' if method != "GET" else 'gresponse.txt', 'w') as f:
            f.write(f"Status Code: {response.status_code}\n")
            f.write("Response Headers:\n")
            for header, value in response.headers.items():
                f.write(f"{header}: {value}\n")
            
            try:
                # Try to parse and pretty print JSON response
                response_json = response.json()
                f.write("\nResponse Body (JSON):\n")
                f.write(json.dumps(response_json, indent=2))
            except ValueError:
                # If not JSON, write raw text
                f.write("\nResponse Body:\n")
                f.write(response.text)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Centralized request handling with error management and logging"""
        full_url = f"{self.base_url}/{endpoint}"
        
        # Log the request details before sending
        self._log_request(method, full_url, **kwargs)
        
        try:
            response = self.session.request(method, full_url, **kwargs)
            
            # Log the response details
            self._log_response(method, response)
            
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")


class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

@dataclass
class User:
    user_name: str
    client: str
    user_courses: List[str] = field(default_factory=list)
    user_modules: List[str] = field(default_factory=list)
    _id: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Question:
    question_content: str
    question_options: Dict[str, str]
    question_answer: str
    difficulty_rating: int
    question_subjects: List[str]
    course: str
    module: str
    _id: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Session:
    user: Union[str, List[str]]
    bank: str
    client: str
    max_score: int
    dynamic: bool = False
    question_list: List[Dict[str, Any]] = field(default_factory=list)
    max_questions: int = None
    starter_difficulty: int = 3

    def to_dict(self):
        data = {k: v for k, v in asdict(self).items() if v is not None}
        if isinstance(data.get('started'), datetime):
            data['started'] = data['started'].isoformat()
        return data

@dataclass
class Draft:
    users: List[str]
    bank: str
    client: str
    max_score: int
    dynamic: bool = False
    question_list: List[Dict[str, Any]] = field(default_factory=list)
    max_questions: int = None
    starter_difficulty: int = 3

    def to_dict(self):
        data = {k: v for k, v in asdict(self).items() if v is not None}
        return data

class LearningPlatformSDK:
    def __init__(self, base_url: str):
        self.client = APIClient(base_url)

    # CLIENT MANAGEMENT
    def create_client(self, client_name: str) -> str:
        """Create a new client database"""
        return self.client._make_request('POST', f'clients/create', params={'client': client_name})

    def delete_client(self, client_uuid: str) -> None:
        """Delete a client database"""
        self.client._make_request('POST', f'{client_uuid}/delete')

    # USER MANAGEMENT
    def create_user(self, client: str, user: User) -> str:
        """Create a user in a specific client database"""
        response = self.client._make_request(
            'POST', 
            f'{client}/users/create', 
            json=user.to_dict()
        )
        return response.get('user_uuid')

    def get_user(self, client: str, user_id: str) -> User:
        """Get user details"""
        user_data = self.client._make_request('GET', f'{client}/users/{user_id}')
        return User(**user_data)

    def get_user_list(self, client:str, courses: List[str] = [], modules: List[str] = []):
        """Get list of users"""
        return(self.client._make_request("POST", f'{client}/users', json = {"courses": courses, "modules": modules}))

    def update_user(self, client: str, user_id: str, user: User) -> None:
        """Update user's courses and modules"""
        self.client._make_request(
            'PUT', 
            f'{client}/users/{user_id}', 
            json={
                'courses': user.user_courses, 
                'modules': user.user_modules
            }
        )

    def delete_user(self, client: str, user_id: str) -> None:
        """Delete a user"""
        self.client._make_request('DELETE', f'{client}/users/{user_id}')

    def get_user_upcoming(self, client: str, user_id: str) -> List[Dict]:
        """Get user's upcoming cards"""
        return self.client._make_request('GET', f'{client}/users/{user_id}/upcoming')

    def get_user_assessments(self, client: str, user_id: str) -> List[Dict]:
        """Get user's assessments"""
        return self.client._make_request('GET', f'{client}/users/{user_id}/assessments')

    def get_user_practice_sessions(self, client: str, user_id: str) -> List[Dict]:
        """Get user's practice sessions"""
        return self.client._make_request('GET', f'{client}/users/{user_id}/practice')

    def get_user_sessions(self, client: str, user_id: str) -> List[Dict]:
        """Get all user sessions"""
        return self.client._make_request('GET', f'{client}/users/{user_id}/sessions')

    # QUESTION BANK MANAGEMENT



    def create_question_bank(self, client: str, bank_name: str, positive_weights: List[float], negative_weights: List[float]) -> str:
        """Create a blank question bank"""
        print({
            "name": bank_name,
            "positive_weights": positive_weights,
            "negative_weights": negative_weights,
            "client": client})
        return self.client._make_request('POST', f'{client}/createbank', json={
            "name": bank_name,
            "positive_weights": positive_weights,
            "negative_weights": negative_weights,
            "client": client
        })

    def get_all_banks(self, client: str) -> List[str]:
        """Get all banks in a client database"""
        return self.client._make_request('GET', f'{client}/banks')

    def get_bank(self, client: str, bank: str) -> List[Question]:
        """Get a complete question bank"""
        bank_data = self.client._make_request('GET', f'{client}/{bank}')
        return bank_data

    def rename_bank(self, client: str, bank: str, new_name: str) -> None:
        """Rename a question bank"""
        self.client._make_request('PUT', f'{client}/{bank}', params={'newname': new_name})

    def delete_bank(self, client: str, bank: str) -> None:
        """Delete a question bank"""
        self.client._make_request('DELETE', f'{client}/{bank}')

    def add_questions(self, client: str, bank: str, questions: List[Question]) -> List[str]:
        """Add questions to a bank"""
        return self.client._make_request(
            'POST', 
            f'{client}/{bank}/add', 
            json=[q.to_dict() for q in questions]
        )

    def upload_bank(self, client: str, bank: str, file_path: str) -> str:
        """Upload questions via Excel/CSV"""
        with open(file_path, 'rb') as file:
            files = {'file': file}
            return self.client._make_request(
                'POST', 
                f'{client}/{bank}/upload', 
                files=files
            )

    def search_questions(
        self, 
        client: str, 
        bank: str, 
        subjects: Optional[List[str]] = None, 
        difficulty: Optional[List[str]] = None, 
        course: Optional[List[str]] = None, 
        module: Optional[List[str]] = None
    ) -> List[Question]:
        """Search questions in a bank"""
        query = {
            'subjects': subjects,
            'difficulty': difficulty,
            'course': course,
            'module': module
        }
        proquery={}
        # Remove None values
        print("pre")
        print(query)
        
        keys = query.keys()
        for i in keys:
            if query[i] != None or query[i] != []:
                proquery[i] = query[i]
        
        print("post")
        print(proquery)

        results = self.client._make_request(
            'POST', 
            f'{client}/{bank}/search', 
            json=query
        )
        return [q for q in results]

    def get_questions_by_id(self, client: str, bank: str, question_ids: List[str]) -> List[Question]:
        """Get specific questions by ID"""
        results = self.client._make_request(
            'POST', 
            f'{client}/{bank}/get', 
            json={'id_list': question_ids}
        )
        return [Question(**q) for q in results]

    def update_questions(self, client: str, bank: str, questions: List) -> None:
        """Update questions in a bank"""
        self.client._make_request(
            'PUT', 
            f'{client}/{bank}/update', 
            json={"questionlist":[q for q in questions]}
        )

    def move_questions(self, client: str, bank: str, question_ids: List[str], new_bank: str) -> None:
        """Move questions between banks"""
        self.client._make_request(
            'PUT', 
            f'{client}/{bank}/move', 
            json={'id_list': question_ids, 'new_bank': new_bank}
        )

    def delete_questions(self, client: str, bank: str, question_ids: List[str]) -> None:
        """Delete specific questions from a bank"""
        self.client._make_request(
            'DELETE', 
            f'{client}/{bank}/delete', 
            json={'id_list': question_ids}
        )

    # ASSESSMENT METHODS
    def create_assessment(self, client: str, user_id: str, session: Session) -> str:
        """Create an assessment"""
        pprint.pprint(session.to_dict())
        return self.client._make_request(
            'POST', 
            f'{client}/assessment/{user_id}/create', 
            json=session.to_dict()
        )

    def start_assessment(self, client: str, session_id: str, shuffle: bool = False) -> List[Dict]:
        """Start an assessment"""
        return self.client._make_request(
            'GET', 
            f'{client}/assessment/{session_id}/start', 
            params={'shuffle': shuffle}
        )

    def submit_assessment(self, client: str, session_id: str, answers: List[Dict]) -> Dict:
        """
        Submit an assessment with improved error handling and payload validation.
        
        Args:
            client (str): The client identifier
            session_id (str): The session ID for the assessment
            answers (List[Dict]): List of answer dictionaries to be submitted
        
        Returns:
            Dict: Response from the API submission
        """
        try:
            # Validate payload structure before sending
            if not answers:
                raise ValueError("Answers list cannot be empty")
            
            # Ensure each answer is a dictionary
            for answer in answers:
                if not isinstance(answer, dict):
                    raise TypeError(f"Each answer must be a dictionary, got {type(answer)}")
            
            # Log the payload for debugging
            print("Submitting assessment payload:")
            print(json.dumps(answers, indent=2))
            
            # Explicitly specify JSON content type and convert to JSON
            return self.client._make_request(
                'POST', 
                f'{client}/assessment/{session_id}/submit', 
                json=answers,  # Use json parameter instead of data
                headers={'Content-Type': 'application/json'}
            )
        
        except (ValueError, TypeError) as validation_error:
            # Log specific validation errors
            print(f"Payload validation error: {validation_error}")
            raise
        except Exception as e:
            # Catch and log any unexpected errors
            print(f"Unexpected error during assessment submission: {e}")
            raise


    def dynamic_assessment_next(
        self, 
        client: str, 
        session_id: str, 
        question_id: str, 
        answer_selection: str
    ) -> Dict:
        """Get next question in dynamic assessment"""
        return self.client._make_request(
            'POST', 
            f'{client}/assessment/{session_id}/next', 
            json={'question_id': question_id, 'answer_selection': answer_selection}
        )

    def delete_assessment(
        self,
        client:str,
        session_id: str
    ) -> Dict:
        """Delete Assessment Session."""
        return self.client._make_request(
            'DELETE',
            f'{client}/assessment/{session_id}/delete'
        )



    # ASSESSMENT DRAFT ENDPOINTS
    def create_draft(self, client:str, draft: Draft ) -> str:
        """Create a assessment draft that can be assigned later."""
        # draftload = {
        #     "users" : [session.user],
        #     "bank": session.bank,
        #     "client": session.client,
        #     "question_list": session.question_list,
        #     "dynamic": session.dynamic,
        #     "max_score": session.max_score,
        #     "max_questions" : session.max_questions,
        #     "starter_difficulty" : session.starter_difficulty
        # }
        draftload = draft.to_dict()
        return self.client._make_request(
            'POST',
            f'{client}/draft',
            json = draftload
        )

    def get_all_drafts(self, client:str) -> dict:   
        """Get all drafts in a client's history"""
        return self.client._make_request(
            "GET",
            f'{client}/drafts/all'
        )
    
    def delete_draft(self,client:str, draft_id:str):
        """Delete a draft"""
        return self.client._make_request(
            "DELETE",
            f"{client}/draft/{draft_id}"
        )

    def update_draft(self,client:str, draft_id: str, nudraft: Draft):
        """Update a draft"""
        return self.client._make_request(
            "PUT",
            f"{client}/draft/{draft_id}",
            json = {nudraft.to_dict()}
        )

    def get_draft(self, client:str, draft_id: str):
        """Get details of one draft"""
        return self.client._make_request(
            "GET",
            f"{client}/draft/{draft_id}"
        )

    def assign_drafts(self, client:str, draft_id:str, userlist:List[str]=[]):
        """Assign drafts to users"""
        
        return self.client._make_request(
            "POST",
            f"{client}/draft/{draft_id}/assign",
            json = {"userlist": userlist}
        )

    # PRACTICE SESSION METHODS
    def create_practice(self, client: str, user_id: str, session: Session) -> str:
        """Create a practice session"""
        return self.client._make_request(
            'POST', 
            f'{client}/practice/{user_id}/create', 
            json=session.to_dict()
        )

    def start_practice(self, client: str, session_id: str) -> Dict:
        """Start a practice session"""
        return self.client._make_request('GET', f'{client}/practice/{session_id}/start')

    def continue_practice(
        self, 
        client: str, 
        session_id: str, 
        answer_selection: str, 
        difficulty_selection: int
    ) -> Dict:
        """Continue a practice session"""
        return self.client._make_request(
            'POST', 
            f'{client}/practice/{session_id}/next', 
            json={
                'answer_selection': answer_selection, 
                'answer_difficulty_selection': difficulty_selection
            }
        )

    def delete_practice(
        self,
        client:str,
        session_id: str
    ) -> Dict:
        """Delete Practice Session."""
        return self.client._make_request(
            'DELETE',
            f'{client}/practice/{session_id}/delete'
        )



# Example Usage
def example_usage():
    # Initialize the SDK
    sdk = wizard.LearningPlatformSDK( st.session_state.api if "api" in st.session_state else "http://localhost:8100")
    
    # Create a client
    client_uuid = sdk.create_client('my_learning_platform')

    # Create a user
    user = User(
        user_name='john_doe', 
        client=client_uuid, 
        user_courses=['course1', 'course2'],
        user_modules=['module1', 'module2']
    )
    user_id = sdk.create_user(client_uuid, user)

    # Create a question bank
    bank_name = sdk.create_question_bank(client_uuid, 'math_questions')

    # Add a question to the bank
    question = Question(
        question_content='What is 2 + 2?',
        question_options={'a': '3', 'b': '4', 'c': '5', 'd': '6'},
        question_answer='b',
        difficulty_rating='1',
        question_subjects=['math', 'basic arithmetic'],
        course='math101',
        module='addition'
    )
    sdk.add_questions(client_uuid, bank_name, [question])