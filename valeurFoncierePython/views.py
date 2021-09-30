from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from valeurFoncierePython.graphics import *
from valeurFoncierePython.forms import *
from django.views.decorators.csrf import csrf_exempt

def get_year(request: HttpRequest):
    return request.GET.get('year', '2020')

@csrf_exempt
def index(request: HttpRequest):
    year = get_year(request)
    
    if request.method == "POST":
        form = DepartementForm(request.POST)
        if form.is_valid():
            departement = form.cleaned_data['departement']
            return HttpResponseRedirect(f'/departement/{departement}?year={year}')

    context = {
        "graphics": [
            #appelle les fonctions du code python de "graphics.py" relative à une année (ensemble de la France)
             Number_SalesPer(clean_datasets[year], 'Code departement', year),
             Number_SalesPer(clean_datasets[year], 'Code postal', year),
             Number_SalesPer(clean_datasets[year], 'Commune', year),

             Communes_Top_Ventes(clean_datasets[year], year, 20),
             AvgPrix_MCSurfaceBati_Dep(clean_datasets[year], year),
             AvgPrice_MCTerrain_Dep(clean_datasets[year], year),
             SurfaceTerrain_NatureCulture(clean_datasets[year], year),
             PorportionTypeBien(clean_datasets[year], year),
             Repartion_TypeLocal(clean_datasets[year], year),
             ValeurFonciere_NatureMutation(clean_datasets[year], year),
             ValeurFonciere_NbPiecesP(clean_datasets[year], year),
             Map_AvgPrice_MCTerrain_Dep(clean_datasets[year], year),
             Map_NombreVente_dep(clean_datasets[year], year),
             Bar_ValeurFonciere_dep(clean_datasets[year], year),

             #NombreVentes_PerYear(clean_datasets),
             #NbrVentesLocal_TimeSeries(clean_datasets, 'Maison'),
             #NbrVentesLocal_TimeSeries(clean_datasets, 'Appartement'),
             #NbrVentesLocal_TimeSeries(clean_datasets, 'Dépendance')


        ],
        "year": year,
        "form": DepartementForm()
    }
    html = render_to_string('index.html', context)
    return HttpResponse(html)

@csrf_exempt
def departement(request : HttpRequest, departement: str):
    year = get_year(request)
    context = {
        "graphics": [
            #appelle des fonctions relatives à un département
            Number_SalesPer_Commune(clean_datasets[year], departement, year),
            AvgPrice_MCTerrain_Commune(clean_datasets[year], departement, year),
            BoxP_ValeurFonciere_dep(clean_datasets[year], year, departement),
            #AvgPrice_MC_Dep(clean_datasets, departement)
            
        ],
        "depart": departement,
        "year": year,
        "form": DepartementForm()
    }
    html = render_to_string('departement.html', context)
    return HttpResponse(html)

@csrf_exempt
def commune_form(request : HttpRequest):
    year = get_year(request)
    if request.method == 'POST':
        form = CommuneForm(request.POST)
        if form.is_valid():
            commune = form.cleaned_data['commune']
            return HttpResponseRedirect(f'/commune/{commune}?year={year}')
    context = {
        "year": year,
        "commune": 'a choisir',
        "form": CommuneForm(),
        "action": 'commune/'
    }
    html = render_to_string('commune.html', context)
    return HttpResponse(html)

@csrf_exempt
def commune(request : HttpRequest, commune: str):
    year = get_year(request)
    context = {
        "graphics": [
            BoxP_ValeurFonciere_commune(clean_datasets[year], year, commune),
            #AvgPrice_MC_Commune(clean_datasets,commune)
            
        ],
        "commune": commune,
        "year": year,
        "form": CommuneForm(),
        "action": 'commune/'
    }
    html = render_to_string('commune.html', context)
    return HttpResponse(html)