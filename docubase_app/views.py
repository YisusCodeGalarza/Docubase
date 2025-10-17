from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Proyecto, Pagina, Comentario, Etiqueta
from .forms import CustomUserCreationForm, ProyectoForm, PaginaForm
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.auth import views as auth_views
from django.http import FileResponse
import os
from django.conf import settings
from .views import netaudit_verify


# --- Vistas principales ---
def netaudit_verify(request):
    filepath = os.path.join(settings.BASE_DIR, 'docubase_app', 'static', 'netaudit-verify.txt')
    return FileResponse(open(filepath, 'rb'), content_type='text/plain')

def index(request):
    """
    Renderiza la página de inicio (landing page).

    Muestra los 3 proyectos públicos más recientes para dar la bienvenida
    a los visitantes.
    """
    # Obtiene los 3 proyectos públicos más recientes
    proyectos_recientes = Proyecto.objects.filter(es_publico=True).order_by('-fecha_actualizacion')[:3]
    context = {'proyectos_recientes': proyectos_recientes}
    return render(request, 'docubase_app/index.html', context)

def proyectos_lista(request):
    """
    Muestra una lista de todos los proyectos públicos.
    """
    proyectos = Proyecto.objects.all()
    context = {'proyectos': proyectos}
    return render(request, 'docubase_app/projects.html', context)

def buscar_proyectos(request):
    """
    Gestiona la búsqueda de proyectos.

    Filtra los proyectos basándose en un término de búsqueda (`query`)
    proporcionado en la URL. La búsqueda se realiza en el título,
    descripción, nombre de autor y etiquetas del proyecto.
    """
    # Obtiene el parámetro 'q' de la URL (ej: /buscar/?q=python)
    query = request.GET.get('q')
    # Filtra usando Q objects para combinar búsquedas con un OR lógico.
    # .distinct() evita resultados duplicados si un proyecto coincide en múltiples campos (ej. título y etiqueta).
    proyectos = Proyecto.objects.filter(
        Q(titulo__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(autor__username__icontains=query) |
        Q(etiquetas__nombre__icontains=query)
    ).distinct()
    # Pasa los proyectos encontrados y la query original a la plantilla.
    context = {
        'proyectos': proyectos,
        'query': query
    }
    return render(request, 'docubase_app/search_results.html', context)

# --- Vistas de Proyectos ---

@login_required
def dashboard(request):
    """
    Muestra el panel de control personal del usuario autenticado.

    Lista todos los proyectos creados por el usuario actual.
    """
    # El decorador @login_required asegura que solo usuarios autenticados puedan acceder.
    proyectos_del_usuario = request.user.proyectos.all()
    context = {'proyectos': proyectos_del_usuario}
    return render(request, 'docubase_app/dashboard.html', context)

@login_required
def crear_proyecto(request):
    """
    Gestiona la creación de un nuevo proyecto.

    Si el método es POST, procesa el formulario. Si es GET, muestra un
    formulario vacío para crear un proyecto.
    """
    if request.method == 'POST':
        # Crea una instancia del formulario con los datos enviados (request.POST) y archivos (request.FILES)
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guarda el formulario, pero no lo confirmes en la BD todavía.
            proyecto = form.save(commit=False) 
            # Asigna el usuario actual como el autor del proyecto.
            proyecto.autor = request.user
            # Ahora form.save() se encargará de guardar el objeto y sus relaciones m2m
            form.save()
            return redirect('dashboard')
    else:
        form = ProyectoForm()

    context = {'form': form, 'titulo_pagina': 'Crear Nuevo Proyecto'}
    return render(request, 'docubase_app/crear_proyecto.html', context)

@login_required
def editar_proyecto(request, proyecto_slug):
    """
    Gestiona la edición de un proyecto existente.

    El usuario solo puede editar los proyectos de los que es autor.
    """
    # Busca el proyecto por su slug y se asegura de que el autor sea el usuario actual.
    # Si no lo encuentra o el autor no coincide, devuelve un error 404.
    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug, autor=request.user)

    if request.method == 'POST':
        # Carga el formulario con los datos enviados y la instancia del proyecto a editar.
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            # El método save() del formulario se encarga de la lógica de guardado.
            # No es necesario `commit=False` aquí porque el autor ya está asignado.
            proyecto_editado = form.save()
            # form.save() se encargará de guardar los cambios y las etiquetas
            return redirect('proyecto_detalle', proyecto_slug=proyecto_editado.slug)
    else:
        form = ProyectoForm(instance=proyecto)
    
    context = {'form': form, 'proyecto': proyecto}
    return render(request, 'docubase_app/editar_proyecto.html', context)

def proyecto_detalle(request, proyecto_slug):
    """
    Muestra los detalles de un proyecto específico y lista sus páginas.

    Accesible para cualquier usuario si el proyecto es público.
    """
    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug)
    paginas = proyecto.paginas.all()
    context = {
        'proyecto': proyecto,
        'paginas': paginas
    }
    return render(request, 'docubase_app/project_detail.html', context)

# --- Vistas de Páginas ---

@login_required
def crear_pagina(request, proyecto_slug):
    """
    Gestiona la creación de una nueva página dentro de un proyecto.
    """
    # Obtiene el proyecto al que pertenecerá la nueva página.
    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug)

    if request.method == 'POST':
        form = PaginaForm(request.POST)
        if form.is_valid():
            # Crea la instancia de la página sin guardarla en la BD.
            pagina = form.save(commit=False)
            # Asigna el proyecto y el autor.
            pagina.proyecto = proyecto
            pagina.autor = request.user
            # Ahora sí, guarda la página en la base de datos.
            pagina.save()
            return redirect('proyecto_detalle', proyecto_slug=proyecto_slug)
    else:
        form = PaginaForm()

    context = {'form': form, 'proyecto': proyecto}
    return render(request, 'docubase_app/crear_pagina.html', context)

@login_required
def editar_pagina(request, proyecto_slug, pagina_slug):
    """
    Gestiona la edición de una página existente.

    El usuario solo puede editar las páginas de las que es autor.
    """
    # Busca la página asegurando que pertenece al proyecto y autor correctos.
    pagina = get_object_or_404(Pagina, slug=pagina_slug, proyecto__slug=proyecto_slug, autor=request.user)

    if request.method == 'POST':
        form = PaginaForm(request.POST, instance=pagina)
        if form.is_valid():
            pagina_editada = form.save(commit=False) # No es estrictamente necesario commit=False aquí.
            pagina_editada.save()
            return redirect('pagina_detalle', proyecto_slug=proyecto_slug, pagina_slug=pagina_editada.slug)
    else:
        form = PaginaForm(instance=pagina)
    
    context = {'form': form, 'pagina': pagina, 'proyecto_slug': proyecto_slug}
    return render(request, 'docubase_app/editar_pagina.html', context)

def pagina_detalle(request, proyecto_slug, pagina_slug):
    """
    Muestra el contenido de una página específica.
    """
    pagina = get_object_or_404(
        Pagina, slug=pagina_slug, proyecto__slug=proyecto_slug)
    context = {'pagina': pagina}
    return render(request, 'docubase_app/page_detail.html', context)

# --- Vistas de Autenticación (las dejamos aquí para que estén organizadas) ---

def register(request):
    """
    Gestiona el registro de nuevos usuarios.

    Si el usuario ya está autenticado, lo redirige al dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # El método save() del formulario se encarga de crear el usuario.
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'docubase_app/register.html', context)