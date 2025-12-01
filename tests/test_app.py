"""
Tests for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from src.app import activities
    
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and intramural play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills on the courts",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lisa@mergington.edu", "thomas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["alexander@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_includes_participant_data(self, client, reset_activities):
        """Test that each activity includes participants list."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert chess_club["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test successfully signing up a new participant."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=new@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "new@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        client.post("/activities/Chess%20Club/signup?email=new@mergington.edu")
        
        response = client.get("/activities")
        chess_participants = response.json()["Chess Club"]["participants"]
        
        assert "new@mergington.edu" in chess_participants
        assert len(chess_participants) == 3
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up an already-registered participant fails."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=new@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes a participant from an activity."""
        # Verify participant exists
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_updates_participants_list(self, client, reset_activities):
        """Test that unregister actually removes from the participants list."""
        # Unregister
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify removal
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" not in participants
        assert len(participants) == 1
        assert participants == ["daniel@mergington.edu"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-existent participant fails."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test the complete flow of signing up and then unregistering."""
        activity_name = "Chess%20Club"
        email = "integration@mergington.edu"
        
        # Initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()["Chess Club"]["participants"]) == initial_count + 1
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()["Chess Club"]["participants"]) == initial_count
        assert email not in response.json()["Chess Club"]["participants"]
