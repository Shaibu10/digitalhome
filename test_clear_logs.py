#!/usr/bin/env python
"""Test the clear old logs functionality"""

import requests
import json
from datetime import datetime, timedelta
from models import UserActivity, User
from extensions import db
from app import app

def test_clear_logs():
    """Test clearing old logs"""
    
    with app.app_context():
        # First, let's create some test old logs
        user = User.query.first()
        if not user:
            print("No users found in database")
            return
        
        # Create activity from 31 days ago
        old_date = datetime.utcnow() - timedelta(days=31)
        old_activity = UserActivity(
            user_id=user.id,
            activity_type='test',
            description='Old test activity',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        old_activity.created_at = old_date
        
        # Create recent activity
        recent_activity = UserActivity(
            user_id=user.id,
            activity_type='test',
            description='Recent test activity',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        db.session.add(old_activity)
        db.session.add(recent_activity)
        db.session.commit()
        
        print(f"Created test activities")
        print(f"Total activities before clearing: {UserActivity.query.count()}")
        
        # Check the activities
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_activities = UserActivity.query.filter(UserActivity.created_at < cutoff_date).all()
        print(f"Activities older than 30 days: {len(old_activities)}")
        for activity in old_activities:
            print(f"  - {activity.created_at}: {activity.description}")

if __name__ == '__main__':
    test_clear_logs()
