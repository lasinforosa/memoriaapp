import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages # <--- Per mostrar missatges d'error
from .forms import RegistreForm
from .models import Jugador, Club
from .filters import JugadorFilter


def llista_jugadors(request):
    queryset = Jugador.objects.all()

    # Lògica d'ordenació
    # Si venim del botó "Netejar filtres", no volem ordenació estranya
    sort = request.GET.get('sort', 'nom_i_cognoms') # Per defecte ordenem per nom

    # Camps vàlids per ordenar (seguretat per evitar errors)
    valid_sorts = ['nom_i_cognoms', 'elo_fide', 'elo_regio', 'categoria', '-elo_fide', '-elo_regio']
    if sort not in valid_sorts:
        sort = 'nom_i_cognoms'

    filter = JugadorFilter(request.GET, queryset=queryset)
    
    # Apliquem l'ordenació al resultat filtrat
    jugadors = filter.qs.order_by(sort)

    # Agafem els paràmetres de la URL per passar-los al botó de Jugar
    # Així el botó sabrà quins filtres estan actius
    query_params = request.GET.copy()
    # Eliminem la pàgina si hi és, per si hi ha paginació en el futur
    # if 'page' in query_params:
    #    query_params.pop('page')
    
    # Codifiquem els paràmetres per posar-los a la URL (ex: ?club=1&sexe=M)
    query_string = query_params.urlencode()

    return render(request, 'core/llista.html', {
        'filter': filter,
        'jugadors': filter.qs,
        'query_string': query_string, # <--- Passem això a la plantilla
        'current_sort': sort # Per saber quina columna està activa
    })

def quiz_club(request):
    # Variables per guardar resultats
    missatge = None
    encert = False
    jugador_actual = None
    opcions = []
    
    # 1. Gestionem la resposta (POST)
    if request.method == 'POST':
        jugador_id = request.POST.get('jugador_id')
        resposta_id = request.POST.get('resposta') # Aquí rebem l'ID del jugador que l'usuari ha clicat
        jugador_actual = get_object_or_404(Jugador, id=jugador_id)
        
        # Comprovem si ha encertat el NOM
        if str(jugador_actual.id) == resposta_id:
            missatge = "¡Correcte! Molt bé!"
            encert = True
        else:
            # Busquem el nom de qui ha dit per donar feedback
            jugador_resposta = Jugador.objects.filter(id=resposta_id).first()
            missatge = f"Error! Era: {jugador_actual.nom_i_cognoms}"
            encert = False

    # 2. Preparar la següent pregunta
    # Apliquem el FILTRE que ve per URL (igual que a la llista)
    base_queryset = Jugador.objects.all()
    filter = JugadorFilter(request.GET, queryset=base_queryset)
    
    # FILTRE CLAU: Només jugadors amb FOTO i que no siguin menors (per seguretat extra)
    # Excloem menors per categories, igual que a la pujada
    jugadors_disponibles = filter.qs.exclude(foto='').exclude(foto__isnull=True)
    # Aquí podries afegir un filtre extra per categoria si vols assegurar-te:
    # jugadors_disponibles = jugadors_disponibles.exclude(categoria__icontains='S14') ...
    
    jugadors_disponibles = filter.qs.exclude(club=None) # Treiem els que no tenen club
    
    # Comprovem si hi ha suficients jugadors
    if jugadors_disponibles.count() < 4:
        return render(request, 'core/quiz.html', {
            'error': 'Necessites almenys 4 jugadors amb foto en aquesta selecció per jugar.', 
            'query_string': request.GET.urlencode()
        })
    
    # Triem un jugador a l'atzar D'AQUESTA SELECCIÓ FILTRADA
    jugador_actual = random.choice(jugadors_disponibles)
    
    # Opcions falses: Noms d'altres jugadors
    # Agafem 3 jugadors diferents de l'actual (per ID)
    jugadors_falsos = list(Jugador.objects.exclude(id=jugador_actual.id).exclude(foto='').exclude(foto__isnull=True))
    # Si vols que les opcions falses siguin del mateix filtre, usa: list(jugadors_disponibles.exclude(id=jugador_actual.id))
    
    if len(jugadors_falsos) < 3:
         return render(request, 'core/quiz.html', {'error': 'No hi ha prou jugadors per crear opcions.'})

    falsos_random = random.sample(jugadors_falsos, 3)

    # Les opcions són objectes Jugador (perquè volem mostrar el nom)
    opcions = falsos_random + [jugador_actual]
    random.shuffle(opcions)

    
    # Guardem els filtres actuals per mantenir-los al passar la pàgina
    query_string = request.GET.urlencode()

    return render(request, 'core/quiz.html', {
        'jugador': jugador_actual,
        'opcions': opcions, # Llista de jugadors
        'missatge': missatge,
        'encert': encert,
        'query_string': query_string
    })

def registre(request):
    if request.method == 'POST':
        form = RegistreForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login després de registrar-se
            return redirect('llista_jugadors')
    else:
        form = RegistreForm()
    return render(request, 'core/registre.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('llista_jugadors')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('llista_jugadors')
    # Si és GET, simplement mostrem la pàgina de logout o redirigim
    return redirect('llista_jugadors')

@login_required
def pujar_foto(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)

    # Agafem la URL de retorn (si ve) per no perdre els filtres
    next_url = request.GET.get('next', 'llista_jugadors')
    
    # --- LÒGICA DE PROTECCIÓ INTEL·LIGENT ---
    es_menor = False

    # 1. Comprovació per EDAT (si en tenim)
    if jugador.edat is not None and jugador.edat < 18:
        es_menor = True

    # 2. Comprovació per CATEGORIA (si no tenim edat o com a reforç)
    # Busquem paraules clau com S14, S16, Sub14, Sub18, etc.
    if jugador.categoria:
        cat_upper = jugador.categoria.upper()
        # Llista de paraules que indiquen menor d'edat
        paraules_menors = ['S14', 'S16', 'S18', 'SUB14', 'SUB16', 'SUB18', 'SUB-14', 'SUB-16', 'SUB-18', 'U14', 'U16', 'U18']
        # Comprovem si alguna d'aquestes paraules és dins la categoria
        if any(paraula in cat_upper for paraula in paraules_menors):
            es_menor = True

    if es_menor:
        messages.error(request, f"No es pot pujar la foto: El jugador '{jugador.nom_i_cognoms}' és menor d'edat o està en categoria juvenil ({jugador.categoria}).")
        return redirect(next_url)
    # -----------------------------------------

    # PROCESSAR EL FORMULARI (POST)
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        if foto:
            jugador.foto = foto
            jugador.pujat_per = request.user
            jugador.save()
            messages.success(request, f"Foto de {jugador.nom_i_cognoms} pujada correctament!")
            return redirect(next_url) # Retornem a la URL amb filtres
        else:
            messages.error(request, "No has seleccionat cap fitxer.")

    return render(request, 'core/pujar_foto.html', {'jugador': jugador, 'next_url': next_url})

def detall_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    
    # Preparem els enllaços externs (URLs)
    # Nota: Les URLS de les federacions poden canviar. Això és un exemple estàndard.
    
    # Enllaç FIDE (si té ID FIDE vàlid)
    link_fide = None
    if jugador.id_fide:
        link_fide = f"https://ratings.fide.com/profile/{jugador.id_fide}"

    # Enllaç FCE (Federació Catalana) - Format habitual
    # Nota: La web de la FCE canvia sovint. Si tens el link exacte, millor.
    # Un format comú és buscar per ID o NOM.
    link_fce = None
    if jugador.id_regio: # Suposem que id_regio és el de la FCE
         link_fce = f"https://www.escacs.cat/jugador/{jugador.id_regio}"
    # Alternativa si no hi ha ID, buscar per nom (codificat URL)
    
    context = {
        'jugador': jugador,
        'link_fide': link_fide,
        'link_fce': link_fce,
    }
    return render(request, 'core/detall_jugador.html', context)
