from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy
from apps.usuario.forms import RegistroForm,UserPasswordResetForm,UserPasswordConfirmForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
# Create your views here.


class RegistroUsuario(CreateView):
    model = User
    template_name = 'usuario/registrar_usuario.html'
    form_class = RegistroForm
    success_url = reverse_lazy('improductivos:improductivos_list')


class LogIn(LoginView):
    template_name = 'usuario/login.html'


class Logout(LogoutView):
	next_page=reverse_lazy('usuario:login')


class PasswordReset(PasswordResetView):
	template_name='usuario/password_reset_form.html'
	email_template_name='usuario/password_reset_email.html'
	html_email_template_name='usuario/password_reset_email.html'
	form_class=UserPasswordResetForm
	protocol='http'
	success_url=reverse_lazy('usuario:password_reset_done')
	
	

class PasswordResetDone(PasswordResetDoneView):
	template_name='usuario/password_reset_done.html'

class PasswordResetConfirm(PasswordResetConfirmView):
	template_name='usuario/password_reset_confirm.html'
	form_class=UserPasswordConfirmForm
	success_url=reverse_lazy('usuario:password_reset_complete')
	

class PasswordResetComplete(PasswordResetCompleteView):
	template_name='usuario/password_reset_complete.html'