from django.urls import path
from .views import Home, Login, Signup, Logout, Dashboard

urlpatterns = [
    path('home', Home.as_view(), name='finance-home'),
    path('login', Login.as_view(), name='finance-login'),
    path('signup', Signup.as_view(), name='finance-signup'),
    path('logout', Logout.as_view(), name='finance-logout'),
    path('dashboard', Dashboard.as_view(), name='finance-dashboard' )
]