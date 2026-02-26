import django_filters
from .models import Jugador
from django.db.models import Q # Necessari per a consultes OR

class JugadorFilter(django_filters.FilterSet):

    nom_i_cognoms = django_filters.CharFilter(lookup_expr='icontains', label='Buscar per nom')
    elo_fide = django_filters.RangeFilter(label='Rang ELO FIDE')

    # --- NOU FILTRE: TÉ FOTO? ---
    TE_FOTO_OPCIONS = [
        ('', 'Tots'),        # Valor buit = mostra tots
        ('si', 'Amb Foto'),  # Només els que tenen foto
        ('no', 'Sense Foto'), # Només els que NO tenen foto
    ]
    te_foto = django_filters.ChoiceFilter(
        choices=TE_FOTO_OPCIONS, 
        method='filter_te_foto', 
        label='Disponibilitat Foto'
    )

    def filter_te_foto(self, queryset, name, value):
        # Si l'usuari selecciona "si", filtrem els que NO tenen foto buida ni nul·la
        if value == 'si':
            return queryset.exclude(foto='').exclude(foto__isnull=True)
        # Si selecciona "no", filtrem els que tenen foto buida O nul·la
        elif value == 'no':
            return queryset.filter(Q(foto='') | Q(foto__isnull=True))
        return queryset

    class Meta:
        model = Jugador
        fields = [
            'sexe', 
            'categoria', 
            'club',
            'club__provincia', # Filtre per província del club
            'club__regio',     # Filtre per regió/comunitat del club
        ]
