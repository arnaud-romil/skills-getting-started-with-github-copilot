"""Tests for the activities endpoints."""

import pytest


def test_get_activities(client):
    """Test fetching all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) > 0


def test_get_activities_contains_required_fields(client):
    """Test that activities have all required fields."""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity_success(client, reset_activities):
    """Test successfully signing up for an activity."""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_activity_not_found(client):
    """Test signing up for a non-existent activity."""
    response = client.post(
        "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client, reset_activities):
    """Test signing up when already registered."""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_adds_participant(client, reset_activities):
    """Test that signup actually adds the participant."""
    # First, check initial participants
    response = client.get("/activities")
    initial_participants = response.json()["Programming Class"]["participants"].copy()
    
    # Sign up a new student
    client.post(
        "/activities/Programming%20Class/signup?email=newstudent@test.edu"
    )
    
    # Check that the student was added
    response = client.get("/activities")
    updated_participants = response.json()["Programming Class"]["participants"]
    assert "newstudent@test.edu" in updated_participants
    assert len(updated_participants) == len(initial_participants) + 1


def test_unregister_from_activity_success(client, reset_activities):
    """Test successfully unregistering from an activity."""
    # michael@mergington.edu is in Chess Club
    response = client.post(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" in data["message"]


def test_unregister_activity_not_found(client):
    """Test unregistering from a non-existent activity."""
    response = client.post(
        "/activities/NonExistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered(client, reset_activities):
    """Test unregistering when not registered."""
    response = client.post(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_removes_participant(client, reset_activities):
    """Test that unregister actually removes the participant."""
    # michael@mergington.edu is in Chess Club
    # First, verify they're there
    response = client.get("/activities")
    assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]
    
    # Unregister
    client.post(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    
    # Check that they were removed
    response = client.get("/activities")
    assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]


def test_signup_then_unregister(client, reset_activities):
    """Test signing up and then unregistering."""
    email = "tempstudent@test.edu"
    activity = "Debate%20Team"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify signup worked
    response = client.get("/activities")
    assert email in response.json()["Debate Team"]["participants"]
    
    # Unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify unregister worked
    response = client.get("/activities")
    assert email not in response.json()["Debate Team"]["participants"]
