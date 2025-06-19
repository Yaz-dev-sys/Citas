from django.db import models
from django.contrib.auth.models import User

from django.db import models


class Areas(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre_area = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'areas'

    def __str__(self):
        return f"{self.nombre_area} ({self.id_area})"    

class UserProfile(models.Model):
    # Relación 1-a-1 con User (extensión)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # Relación 1-a-1 con Areas
    area = models.ForeignKey(
        Areas,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfiles"
    )
    
    # Otros campos personalizados (ej: teléfono, foto, etc.)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Citas(models.Model):
    id_cita = models.AutoField(primary_key=True)
    id_area = models.ForeignKey(Areas, models.DO_NOTHING, db_column='id_area')
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    motivo = models.TextField(blank=True, null=True)
    codigo_confirmacion = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    comentarios=models.CharField(max_length=250,db_column='comentarios', null=True, blank=True )

    class Meta:
        managed = False
        db_table = 'citas'


class Configuracion(models.Model):
    id_config = models.AutoField(primary_key=True)
    clave = models.CharField(unique=True, max_length=50)
    valor = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'configuracion'


class DiasNoLaborables(models.Model):
    id_dia = models.AutoField(primary_key=True)
    fecha = models.DateField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    id_area = models.ForeignKey(Areas, models.DO_NOTHING, db_column='id_area', blank=True, null=True, db_comment='NULL significa que aplica a todas las áreas')
    recurrente = models.IntegerField(blank=True, null=True, db_comment='Si se repite cada año')

    class Meta:
        managed = False
        db_table = 'dias_no_laborables'
        unique_together = (('fecha', 'id_area'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocumentosCitas(models.Model):
    id_documento = models.AutoField(primary_key=True)
    id_cita = models.ForeignKey(Citas, models.DO_NOTHING, db_column='id_cita')
    nombre_archivo = models.CharField(max_length=255)
    ruta_archivo = models.CharField(max_length=255)
    hash_archivo = models.CharField(max_length=64, db_comment='Para verificar integridad')
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documentos_citas'


class Empleados(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    id_area = models.ForeignKey(Areas, models.DO_NOTHING, db_column='id_area')
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    rol = models.CharField(max_length=11)
    activo = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleados'


class HorariosLaborales(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_area = models.ForeignKey(Areas, models.DO_NOTHING, db_column='id_area')
    dia_semana = models.IntegerField(db_comment='1=Lunes, 2=Martes,...,7=Domingo')
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    duracion_cita = models.IntegerField(db_comment='Duración en minutos')
    max_citas_dia = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'horarios_laborales'
        unique_together = (('id_area', 'dia_semana'),)


class LogsAcceso(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_usuario = models.IntegerField(blank=True, null=True, db_comment='Puede ser usuario o empleado')
    tipo_usuario = models.CharField(max_length=9, blank=True, null=True)
    accion = models.CharField(max_length=50)
    detalles = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'logs_acceso'


class Tramites(models.Model):
    id_tramite = models.AutoField(primary_key=True)
    nombre_tramite = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    requisitos = models.TextField(blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)
    tiempo_estimado = models.CharField(max_length=50, blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    id_area = models.ForeignKey(Areas, models.DO_NOTHING, db_column='id_area')
    activo = models.IntegerField(blank=True, null=True)
    formato_descargable = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tramites'


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    token_verificacion = models.CharField(max_length=100, blank=True, null=True)
    email_verificado = models.IntegerField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'

