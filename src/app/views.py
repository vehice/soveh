from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from accounts.models import *

@login_required
def home(request):
    return render(request, "app/home.html",{
})

@login_required
def show_users(request):
    users = User.objects.all()
    usuarios = []
    for usuario in users:
        aux = {'user': usuario.first_name.title() + " " + usuario.last_name.title(),
        'email': usuario.email,'id': usuario.id, 'estado': usuario.is_active, 'admin': usuario.is_superuser}
        usuarios.append(aux)
    return render(request, 'app/users.html',{'users':usuarios})

@login_required
def show_empresas(request):
    return render(request, 'app/empresas.html',{})

@login_required
def show_analisis(request):
    return render(request, 'app/analisis.html',{})