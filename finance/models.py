from django. db import models
from django.contrib. auth.models import User

# Remove the Login and Signup models - they're not needed! 
# Django's built-in User model handles this already

# If you need additional user information, create a Profile model: 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any extra fields you need
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)