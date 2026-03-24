import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    
    # Delete if exists
    User.objects.filter(username=username).delete()
    
    # Create
    user = User.objects.create_user(username, email, password)
    print(f"User {username} created successfully.")

if __name__ == "__main__":
    create_test_user()
