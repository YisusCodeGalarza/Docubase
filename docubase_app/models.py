from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class Etiqueta(models.Model):
    """
    Representa una etiqueta o categoría para agrupar proyectos o páginas.
    Ejemplos: 'Python', 'Django', 'API', 'Tutorial'.
    """
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        """Representación en cadena del modelo, muestra el nombre de la etiqueta."""
        return self.nombre

class Proyecto(models.Model):
    """
    Representa un proyecto, que es el contenedor principal para la documentación.
    Un proyecto puede tener múltiples páginas y está asociado a un autor.
    """
    titulo = models.CharField(max_length=200)
    # El slug es una versión del título amigable para URLs. Se genera automáticamente.
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    # Imagen de portada opcional para el proyecto.
    imagen = models.ImageField(upload_to='proyectos_imagenes/', blank=True, null=True)
    # Descripción enriquecida usando CKEditor.
    descripcion = RichTextField(blank=True, null=True)
    # El usuario que creó el proyecto. Si se borra el usuario, se borran sus proyectos.
    autor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='proyectos')
    # Relación muchos-a-muchos con las etiquetas. Un proyecto puede tener varias.
    etiquetas = models.ManyToManyField('Etiqueta', blank=True, related_name='proyectos')
    # Timestamps para la creación y última actualización.
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    # Controla si el proyecto es visible para todos o solo para el autor.
    es_publico = models.BooleanField(default=True)
    # Nombre de un ícono (ej. de FontAwesome) para representar el proyecto.
    icono = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        """Representación en cadena, muestra el título del proyecto."""
        return self.titulo

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar un slug único antes de guardar.
        """
        # Si el objeto es nuevo y no tiene slug, lo genera a partir del título.
        if not self.slug:
            self.slug = slugify(self.titulo)
        
        # Lógica para asegurar que el slug sea único.
        # Si ya existe un proyecto con este slug (excluyendo el propio objeto si se está actualizando),
        # se le añade un sufijo numérico.
        original_slug = self.slug
        num = 1
        # .exclude(pk=self.pk) es crucial para evitar conflictos al guardar un objeto existente.
        while Proyecto.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f'{original_slug}-{num}'
            num += 1
        
        super().save(*args, **kwargs)


class Pagina(models.Model):
    """
    Representa una página individual de contenido dentro de un proyecto.
    Puede ser un artículo, un tutorial, una guía, etc.
    """
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    # Contenido principal de la página, editable con CKEditor.
    contenido = RichTextField(blank=True, null=True)
    # El usuario que creó la página.
    autor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='paginas')
    # El proyecto al que pertenece esta página.
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='paginas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    es_publica = models.BooleanField(default=True)
    etiquetas = models.ManyToManyField(Etiqueta, related_name='paginas')

    def save(self, *args, **kwargs):
        """
        Genera un slug único basado en el título de la página antes de guardar.
        """
        if not self.slug:
            self.slug = slugify(self.titulo)

        # Lógica para asegurar que el slug sea único.
        original_slug = self.slug
        num = 1
        while Pagina.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f'{original_slug}-{num}'
            num += 1

        super().save(*args, **kwargs)

    def __str__(self):
        """Representación en cadena, muestra el título de la página."""
        return self.titulo

class Archivo(models.Model):
    """
    Representa un archivo (como una imagen o un documento) que puede ser
    adjuntado a una página o proyecto.
    """
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='archivos/')
    subido_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='archivos')
    subido_en = models.DateTimeField(auto_now_add=True)
    # Un archivo puede estar asociado opcionalmente a una página.
    pagina = models.ForeignKey(
        Pagina, on_delete=models.CASCADE, related_name='archivos', blank=True, null=True)

    def __str__(self):
        return self.nombre

# 5. Modelo para los Comentarios
class Comentario(models.Model):
    """
    Permite a los usuarios dejar comentarios en las páginas de documentación.
    Soporta comentarios anidados (respuestas).
    """
    texto = models.TextField()
    # El autor del comentario.
    autor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comentarios')
    # La página donde se realizó el comentario.
    pagina = models.ForeignKey(
        Pagina, on_delete=models.CASCADE, related_name='comentarios')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Permite anidar comentarios. Si se borra el comentario padre, la respuesta
    # no se borra, sino que su campo `comentario_padre` se establece en NULL.
    comentario_padre = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='respuestas')

    def __str__(self):
        """Representación en cadena para identificar el comentario en el admin."""
        return f"Comentario de {self.autor.username} en {self.pagina.titulo}"
