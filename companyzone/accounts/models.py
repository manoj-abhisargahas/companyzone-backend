from django.db import models
from django.contrib.auth.models import AbstractUser

class AppUser(AbstractUser):
    # The distinction flag for third-party consumers
    is_api_user = models.BooleanField(
        default = False,
        help_text = "Designates whether this account belongs to an external application/API developer."
    )

    class Meta:
        verbose_name = 'AppUser' # Singular name (when editing one user)
        verbose_name_plural = 'AppUsers' # Plural name (this fixes the sidebar title in Django admin)
    
    def __str__(self):
        return self.username
    
# By using class AppUser(AbstractUser):, 
# your database table automatically gets these exact fields out of the box:
#   username (String field for login)
#   password (Encrypted string field)
#   email
#   first_name
#   last_name
#   is_active
#   date_joined

