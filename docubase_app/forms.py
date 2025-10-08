from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proyecto, Pagina, Etiqueta
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProyectoForm(forms.ModelForm):
    descripcion = forms.CharField(
        widget=CKEditorWidget()
    )
    tags_texto = forms.CharField(
        label="Etiquetas (separadas por comas)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Proyecto
        fields = ['titulo', 'imagen', 'descripcion', 'tags_texto', 'icono', 'es_publico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['tags_texto'] = ', '.join(tag.nombre for tag in self.instance.etiquetas.all())

    def save(self, commit=True):
        # Llama al save() original, pero sin guardar las relaciones m2m todavía
        instance = super().save(commit=commit)

        if commit:
            # Limpiamos las etiquetas existentes
            instance.etiquetas.clear()
            # Obtenemos las nuevas etiquetas del campo 'tags_texto'
            tags_texto = self.cleaned_data.get('tags_texto', '')
            if tags_texto:
                tags_list = [tag.strip() for tag in tags_texto.split(',') if tag.strip()]
                for tag_name in tags_list:
                    etiqueta, created = Etiqueta.objects.get_or_create(nombre=tag_name)
                    instance.etiquetas.add(etiqueta)

        return instance

class PaginaForm(forms.ModelForm):
    class Meta:
        model = Pagina
        fields = ['titulo', 'contenido']
        widgets = {'titulo': forms.TextInput(attrs={'class': 'form-control'})}