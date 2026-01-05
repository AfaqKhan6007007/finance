from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import View
from .forms import LoginForm, SignupForm

class Home(View):
    def get(self, request):
        return render(request, 'finance/home.html', {})
    
class Login(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'finance/login.html', {'form':form})
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect('finance-home')

        return render(
            request,
            'finance/login.html',
            {'form': form}
        )
class Signup(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'finance/signup.html', {'form':form})
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            return redirect('finance-home')

        return render(
            request,
            'finance/signup.html',
            {'form': form}
        )
# Create your views here.
