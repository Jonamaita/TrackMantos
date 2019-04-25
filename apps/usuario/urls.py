from django.urls import path, include
from apps.usuario.views import RegistroUsuario, LogIn, Logout, PasswordReset, PasswordResetDone, PasswordResetConfirm, PasswordResetComplete
from django.contrib.auth import views as auth_views

app_name = 'usuario'

urlpatterns = [
    #path('', RegistroUsuario.as_view(), name='index'),
    path('', LogIn.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('reset/password_reset', PasswordReset.as_view(), name='password_reset'),
    path('reset/password_reset_done',
         PasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),
    path('reset/password_reset_complete',
         PasswordResetComplete.as_view(), name='password_reset_complete'),

]
