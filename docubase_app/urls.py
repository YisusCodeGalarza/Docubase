from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # URLs de la página de inicio y lista de proyectos
    path('netaudit-verify.txt', netaudit_verify),
    path('', views.index, name='index'),
    path('proyectos/', views.proyectos_lista, name='proyectos_lista'),

    # URLs de autenticación
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='docubase_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='docubase_app/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='docubase_app/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='docubase_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='docubase_app/password_reset_complete.html'), name='password_reset_complete'),

    # URLs del panel de control
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de proyectos (ordenadas de más específica a más general)
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/<slug:proyecto_slug>/editar/', views.editar_proyecto, name='editar_proyecto'),
    
    # URLs de páginas (ordenadas de más específica a más general)
    path('proyectos/<slug:proyecto_slug>/crear-pagina/', views.crear_pagina, name='crear_pagina'),
    path('proyectos/<slug:proyecto_slug>/<slug:pagina_slug>/editar/', views.editar_pagina, name='editar_pagina'),
    path('proyectos/<slug:proyecto_slug>/<slug:pagina_slug>/', views.pagina_detalle, name='pagina_detalle'),

    # La URL de detalle de proyecto va al final para que no cause conflictos
    path('proyectos/<slug:proyecto_slug>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('buscar/', views.buscar_proyectos, name='buscar_proyectos'),
]