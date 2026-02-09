from rest_framework import serializers
from quejas.models import Queja
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField

class QuejaSerializer(serializers.ModelSerializer):

    autor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())    #Quitar esta linea en produccion
    categoria = serializers.PrimaryKeyRelatedField(queryset=Queja._meta.get_field('categoria').remote_field.model.objects.all())
    distrito = serializers.PrimaryKeyRelatedField(queryset=Queja._meta.get_field('distrito').remote_field.model.objects.all())
    categoria_nombre = SerializerMethodField(read_only=True)
    distrito_nombre = SerializerMethodField(read_only=True)
    autor_nombre = SerializerMethodField(read_only=True)
    class Meta:
        model = Queja
        fields = [
            'id', 
            'titulo', 
            'descripcion', 
            'categoria', 
            'categoria_nombre',
            'distrito', 
            'distrito_nombre',
            'estado', 
            'ubicacion', 
            'autor', 
            'autor_nombre',
            'fecha_creacion', 
            'fecha_actualizacion',
            'num_votos', 
            'num_comentarios', 
            'num_comentarios_top_level']
        read_only_fields = [
            'id', 
            'estado',
            'autor',
            'fecha_creacion', 
            'fecha_actualizacion', 
            'num_votos', 
            'num_comentarios', 
            'num_comentarios_top_level'
        ]
        
    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
#        if not user or not user.is_authenticated:
#            raise serializers.ValidationError("No se puede crear una queja sin estar autenticado.")
        validated_data.setdefault("autor", user)
        validated_data.setdefault("estado", "PENDIENTE")
        return super().create(validated_data)
    
    def validate_titulo(self, value):
        if len(value) < 5 or len(value) > 200:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres y no más de 200.")
        if not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío o contener solo espacios en blanco.")
        return value
    def validate_descripcion(self, value):
        if len(value) < 10 or len(value) > 5000:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres y no más de 5000.")
        return value
    def validate(self, data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and Queja.objects.filter(
            #autor=user,
            titulo=data.get('titulo'),
            distrito=data.get('distrito')
        ).exists():
            raise serializers.ValidationError("Ya has presentado una queja con el mismo título en este distrito.")
        return data
    def get_categoria_nombre(self, obj):
        return getattr(obj.categoria, 'nombre', None)
    def get_distrito_nombre(self, obj):
        return getattr(obj.distrito, 'nombre', None)
    def get_autor_nombre(self, obj):
        return f"{obj.autor.first_name} {obj.autor.last_name}".strip() if obj.autor else None
    
    
        
        

