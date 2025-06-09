from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views import generic
from django.urls import reverse_lazy
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfileForm

# Create your views here.
def login(request):
    return render(request, 'login.html', {})

def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/')

def logout_page(request):
    return render(request, 'logout_user.html')


# Register View
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'
    

class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('user-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileForm(self.request.POST)
        else:
            context['profile_form'] = ProfileForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        
        if form.is_valid() and profile_form.is_valid():
            self.object = form.save()
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
            return HttpResponseRedirect(self.get_success_url())
        
        return self.render_to_response(self.get_context_data(form=form))

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('user-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileForm(
                self.request.POST, 
                instance=self.object.profile
            )
        else:
            context['profile_form'] = ProfileForm(
                instance=self.object.profile
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        
        if form.is_valid() and profile_form.is_valid():
            self.object = form.save()
            profile_form.save()
            return HttpResponseRedirect(self.get_success_url())
        
        return self.render_to_response(context)
    
    