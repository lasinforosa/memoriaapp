from django.contrib import admin
from .models import Club, Jugador
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Definim com mapejar el CSV al Model Jugador
class JugadorResource(resources.ModelResource):
    # Mapeig del Club: Busca el nom, si no existeix, el crea
    club = fields.Field(
        column_name='Club',
        attribute='club',
        widget=ForeignKeyWidget(Club, 'nom')
    )
    
    # Mapeig manual de columnes del CSV a camps del Model
    nom_i_cognoms = fields.Field(column_name='Nom', attribute='nom_i_cognoms')
    id_regio = fields.Field(column_name='Codi', attribute='id_regio')
    elo_regio = fields.Field(column_name='Elo Std.', attribute='elo_regio')
    categoria = fields.Field(column_name='Categoria', attribute='categoria')
    titol = fields.Field(column_name='Títol', attribute='titol')
    sexe = fields.Field(column_name='Sexe', attribute='sexe')
    
    # Configurem quins camps volem importar
    class Meta:
        model = Jugador
        import_id_fields = ('id_regio',) # Usem el Codi FIDE com a identificador únic
        skip_unchanged = True
        # Excloem camps que no venen al CSV o es calculen sols
        exclude = ('id', 'foto', 'data_naixement', 'elo_fide', 'id_fide', 'pujat_per') 

    # Funció per crear el club si no existeix durant la importació
    def before_import_row(self, row, **kwargs):
        nom_club = row.get('Club')
        if nom_club:
            # get_or_create: Busca'l, i si no hi és, crea-lo
            Club.objects.get_or_create(nom=nom_club)
        super().before_import_row(row, **kwargs)

@admin.register(Club)
class ClubAdmin(ImportExportModelAdmin):
    list_display = ('nom', 'provincia', 'regio', 'pais') # Columnes visibles
    search_fields = ('nom', 'provincia') # Barra de cerca
    list_filter = ('regio', 'provincia') # Filtres laterals

@admin.register(Jugador)
class JugadorAdmin(ImportExportModelAdmin):
    resource_class = JugadorResource
    
    # Columnes que es veuen a la llista
    list_display = ('nom_i_cognoms', 'club', 'elo_fide', 'elo_regio', 'categoria', 'sexe')
    
    # Barra de cerca: busca per nom o per nom del club
    search_fields = ('nom_i_cognoms', 'club__nom', 'id_fide')
    
    # Filtres laterals
    list_filter = ('club', 'categoria', 'sexe')

    # Edició ràpida (sense entrar al detall) per alguns camps
    list_editable = ('categoria', 'sexe')