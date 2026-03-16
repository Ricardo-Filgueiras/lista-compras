from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Bem-vindo, {user.username}!')
        return redirect('shopping:index')
    return render(request, 'shopping/register.html', {'form': form})
