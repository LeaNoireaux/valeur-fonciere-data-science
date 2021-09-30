# # Projet PYTHON Code du Notebook
# Léa NOIREAUX, Amine MOUSSA, Cécile PAILHE
# 
 
# # Libraries
# essential libraries
import json
import random
from urllib.request import urlopen

# File reading
import glob
from os import name, read
from os.path import basename, splitext

# storing and anaysis
import numpy as np
import pandas as pd

# visualization
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.offline import plot, iplot, init_notebook_mode
#import calmap
#import folium

# converter
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()   

from mpld3 import fig_to_html

# hide warnings
import warnings
warnings.filterwarnings('ignore')

with open('data/departements-avec-outre-mer.geojson.txt', 'r') as json_file:
        departement = json.load(json_file)

 
# # Import Dataset 
# importing datasets
def data_generator(folder_name):
    filepath = glob.glob(folder_name + "/*")
    for file in filepath:  # for each file
        filename = splitext(basename(file))[0] + ".txt"  # File name
        yield filename, pd.read_csv(folder_name + "/" + filename, sep="|")

 
# # Data Cleaning
def data_cleaning(data, perc_NaN):
    print("Processing cleaning...")
    num_cols = len(data.columns)
    print("\n*" + str(data.isna().sum()))

    # drop cols with "n%" of NaN and their NaN rows
    print("\n* Dropping columns with more then " + str(perc_NaN) + "% of NaN")
    min_count =  int(((100-perc_NaN)/100)*data.shape[0] + 1)
    data = data.dropna(axis=1, thresh=min_count)
    print("-> " + str(num_cols - len(data.columns)) + " columns dropped!")
    print("\n* Number of NaN after the first cleaning in the " + str(len(data.columns)) + " columns left:\n" + str(data.isna().sum()))
    data = data.dropna()
    return data



#Ajoute un 0 devant les code de département qui ont qu'un digit
def add0CodeDep(code):
    if len(code)==1:
        code='0'+code
    return code

def convert_data(data):
    # Convert columns
    data["Code commune"] = data['Code commune'].apply(lambda x: str(int(x)))

    data['Code departement']= data['Code departement'].apply(lambda x: str(x))
    data['Code departement'] = data['Code departement'].apply(add0CodeDep)

    data["Code postal"] = data["Code postal"].apply(lambda x: int(x))
    data['Code postal'] = data['Code postal'].apply(lambda x: str(int(x)))

    data['Valeur fonciere']=data['Valeur fonciere'].apply(lambda x: float('.'.join(x.split(','))))

    data['Prix MC ST']=data['Valeur fonciere']/data['Surface terrain'] 
    data['Prix MC ST']=data['Prix MC ST'].apply(lambda x : 0 if x== np.inf else x)
    data['Prix MC SRB']=data['Valeur fonciere']/data['Surface reelle bati'] 
    data['Prix MC SRB']=data['Prix MC SRB'].apply(lambda x : 0 if x== np.inf else x)
    
    data['Nombre de vente']=1 #crée une colonne pour le nombre de vente remplie de 1 
    return data

 
# # Main
# Create a dictionnary with clean datasets
clean_datasets = {
    
}
for filename, data in data_generator("data/Valeurs Foncieres"):
    # Extract year from filename
    year = ''.join([ch for ch in filename if ch in '0123456789'])
    # Clean data by dropping useless cols and rows / Converting values
    clean_data = data_cleaning(data, perc_NaN=50)
    clean_data = convert_data(clean_data)
    clean_datasets[year] = clean_data

 
# # **Interprétations et visualisations autour d'une année (en particulier 2020)** 
# ## *1) Nombre de vente en fonction de l'année (par département, ville, commune)* ## 
# ### Par departement
def Number_SalesPer(data, column, year):
    X=data.groupby([column])[column].count() #count the number of sale/department (each time a department appear, sale ++
    txt = "Nombre de ventes par " + column + " en " + year
    figure=px.bar(X, barmode='relative',color=X, color_discrete_sequence=px.colors.qualitative.G10, title=txt,height=600, width=1000, labels=[column, "Nombre de ventes"])
    #color_discrete_sequence= px.colors.sequential.Plasma_r
    #figure.show()
    return figure.to_html()


def Number_SalesPer_Commune(data, departement, year):
    data['Nombre de vente']=1
    Y=data[(data['Code departement'] == departement)] #prend que les lignes du département concerné   
    X=Y.groupby(['Commune'])['Nombre de vente'].count().reset_index() #trouve le nombre de vente par commune du département   
    txt = "Nombre de vente par commune du " + departement + " en "  + year
    figure=px.treemap(X, path=['Commune'], values='Nombre de vente',color_discrete_sequence = px.colors.qualitative.Dark2, title=txt,height=600, width=1000)
    figure.data[0].textinfo = 'label+value' #pour afficher le nom de la commune et le nombre de vente
    #figure.show()
    return figure.to_html()


def Communes_Top_Ventes(data, year, n, hover_data=[]):
    data['Nombre de vente']=1
    b=data.groupby(['Commune'])['Nombre de vente'].count().reset_index() #trouve le nombre de vente par commune du département   
    fig = px.bar(b.sort_values('Nombre de vente', ascending=True).tail(n), 
                 x='Nombre de vente', y="Commune", color='Nombre de vente',  
                 text='Commune', orientation='h', width=700, hover_data=hover_data,
                 color_discrete_sequence = px.colors.qualitative.Dark2)
    fig.update_layout(title='Top des communes avec le plus de ventes en France en ' + year, xaxis_title="", yaxis_title="", 
                      yaxis_categoryorder = 'total ascending',
                      uniformtext_minsize=8, uniformtext_mode='hide')
    return fig.to_html()


def AvgPrix_MCSurfaceBati_Dep(data, year):
    X=data.groupby(['Code departement'])['Prix MC SRB'].mean()
    txt = "Prix moyen du mètre carré de la surface réelle bâtie par département en " + year
    figure=px.bar(X, color=X, barmode='relative',color_discrete_sequence=px.colors.qualitative.G10, title=txt,height=600, width=1000)
    return figure.to_html()


def AvgPrice_MCTerrain_Dep(data, year):
    X=data.groupby(['Code departement'])['Prix MC ST'].mean()
    txt = "Prix moyen du mètre carré de la surface de terrain par département en " + year 
    figure=px.bar(X, color=X, barmode='relative',color_discrete_sequence=px.colors.qualitative.G10, title=txt,height=600, width=1000)
    return figure.to_html()

def AvgPrice_MCTerrain_Commune(data, departement, year):
    Y=data[(data['Code departement'] == departement)] #prend que les lignes du département concerné   
    X=Y.groupby(['Commune'])['Prix MC ST'].mean()    
    txt = "Prix moyen du mètre carré de la surface de terrain par commune du " + departement + " en " + year
    figure=px.bar(X, color=X, barmode='relative',color_discrete_sequence=px.colors.qualitative.G10, title=txt,height=600, width=1000)
    return figure.to_html()


def SurfaceTerrain_NatureCulture(data, year):
    d = data.copy()
    d= d.replace('', np.nan).fillna(0)
    d.drop(d[d['Nature culture'] ==0].index, inplace = True)
    txt = "Surface des terrains en fonction de la nature des cultures en " + year
    fig = px.treemap(d, path=["Nature culture"], values="Surface terrain", height=500, width=1000, title=txt, color_discrete_sequence = px.colors.qualitative.Dark2)
    fig.data[0].textinfo = 'label+text+value'
    return fig.to_html()



### 7) Proportion type de bien ### (new)
def PorportionTypeBien(data, year):
    fig = px.pie(data, names="Nature mutation", height=700, width= 1000, title="proportion des types de bien en " + year)
    return fig.to_html()



### 8) Répartition par type de local ### (new)
def Repartion_TypeLocal(data, year):  
    X=data.groupby(by='Type local').size().reset_index(name='total')
    txt = 'Répartition par type de local en ' + year
    fig = px.treemap(X,title=txt, path=["Type local"], values='total', height=400, width=1000, color_discrete_sequence=['red','orange', 'gold', 'yellow'])
    fig.data[0].textinfo = 'label+value'
    return fig.to_html()


def ValeurFonciere_NatureMutation(data, year):
    df=data.copy()
    df.drop(df[df['Nature mutation'] ==0].index, inplace = True)
    df.drop(df[df['Valeur fonciere'] >=1500000].index, inplace = True)
    df["Nature mutation"] = df["Nature mutation"].astype(str)
    df["Date mutation"]=pd.to_datetime(df["Date mutation"], format="%d/%m/%Y")
    df.sort_values(by='Date mutation')
    txt='Valeur fonciere par nature de mutation en ' + year
    fig = px.scatter(df[::100], title=txt, x="Date mutation",y="Valeur fonciere",color="Nature mutation", height=600, width=1150)
    return fig.to_html()

def ValeurFonciere_NbPiecesP(data, year):
    df = data.copy()
    df.drop(df[df['Nombre pieces principales'] ==0].index, inplace = True)
    df.drop(df[df['Valeur fonciere'] >=1500000].index, inplace = True)
    txt='Valeur fonciere par nombre de piece en ' + year
    fig = px.scatter(df[::100],title=txt, x="Valeur fonciere",y="Nombre pieces principales", color= "Valeur fonciere", height=600, width=1000)
    return fig.to_html()



no_departement_map = {}
for feature in departement["features"]:
    feature["id"] = feature["properties"]["nom"]    
    no_departement_map[feature["properties"]["code"]] = feature["id"]



def Map_AvgPrice_MCTerrain_Dep(data, year):
    X=data.groupby(['Code departement'])['Prix MC ST'].mean().reset_index() 
    X["id"]=X["Code departement"].apply(lambda x: no_departement_map[x])
    txt = "Prix moyen du mètre carré de la surface de terrain par département en France en " + year
    fig = px.choropleth(X, color='Prix MC ST', locations = 'id', geojson=departement, scope='europe', color_continuous_scale="RdGy",title=txt)
    return fig.to_html()

def Map_NombreVente_dep(data, year):
    X=data.groupby(['Code departement'])['Nombre de vente'].count().reset_index() #trouve le nombre de vente par département   
    X["id"]=X["Code departement"].apply(lambda x: no_departement_map[x]) 
    txt = 'Nombre ventes par département en ' + year
    fig = px.choropleth(X, color='Nombre de vente', locations = 'id', geojson=departement, scope='europe', color_continuous_scale="RdGy", title=txt, height=600, width= 1000)
    return fig.to_html()

def Bar_ValeurFonciere_dep(data, year):  
   txt = 'Distribution de la valeur fonciere dans les départements de France en ' + year
   figure= px.box(data, x='Code departement', y='Valeur fonciere', points=False,color='Code departement', title=txt, height=600,   width=1000)
   return figure.to_html()

def BoxP_ValeurFonciere_dep(data, year, departement):
    X=data[(data['Code departement'] == departement)]
    txt = 'Distribution de la valeur fonciere dans le ' + departement + " en " + year
    figure= px.box(X, x='Code departement', y='Valeur fonciere', points=False,color='Code departement',title=txt, height=600, width=1000)
    return figure.to_html()

def BoxP_ValeurFonciere_commune(data, year, commune):
    X=data[(data['Commune'] == commune)]
    txt = "Distribution de la valeur fonciere à " + commune + " de France en " + year
    figure= px.box(X, x='Commune', y='Valeur fonciere', points=False,color='Commune', title=txt, height=600, width=1000)
    return figure.to_html()


def Moustache_NbrPiece_SRBatie(data, year):
    df=data.copy()[::100]
    df.drop(df[df['Nombre pieces principales'] ==0].index, inplace = True)
    df.drop(df[df['Nombre pieces principales'] >10].index, inplace = True)
    txt = "Nombre de piece principales par surface reelle batie en " + year
    fig = px.box(df, x="Nombre pieces principales", y="Surface reelle bati", title=txt, height=600, width=1000)
    return fig


def NombreVentes_PerYear(dataset):
    b=pd.DataFrame({'Nombre de vente': [len(dataset["2016"]),
                                        len(dataset["2017"]),
                                        len(dataset["2018"]),
                                        len(dataset["2019"]),
                                        len(dataset["2020"])],
                    'Annee':['2016', '2017', '2018', '2019', '2020']})
    figure = plt.figure()
    plt.bar(x=b['Annee'], y=b['Nombre de vente'], height=100)
    #b.plot.bar(x='Annee',rot=0, title="Nombre de vente par année")
    return fig_to_html(figure)

def NbrVentesLocal_TimeSeries(dataset, type_local):
    a=len(dataset["2016"][(dataset["2016"]['Type local'] == type_local)])
    b=len(dataset["2017"][(dataset["2017"]['Type local'] == type_local)])
    c=len(dataset["2018"][(dataset["2018"]['Type local'] == type_local)])
    d=len(dataset["2019"][(dataset["2019"]['Type local'] == type_local)])
    e=len(dataset["2020"][(dataset["2020"]['Type local'] == type_local)])
    
    txt = "Nombre de vente de " + type_local + " par année"
    b=pd.DataFrame({txt: [a,b,c,d,e],'Annee':['2016', '2017', '2018', '2019', '2020']})
    figure = plt.figure()
    b.plot.bar(x='Annee',rot=0, title=txt)
    return fig_to_html(figure)
    
def AvgPrice_MC_Dep(dataset, departement):    
    a=dataset["2016"].groupby(['Code departement'])['Prix MC ST'].mean()
    b=dataset["2017"].groupby(['Code departement'])['Prix MC ST'].mean()
    c=dataset["2018"].groupby(['Code departement'])['Prix MC ST'].mean()
    d=dataset["2019"].groupby(['Code departement'])['Prix MC ST'].mean()
    e=dataset["2020"].groupby(['Code departement'])['Prix MC ST'].mean()
    
    txt = "Prix moyen du MC dans le " + departement + " sur les 5 ans"
    b=pd.DataFrame({txt: [a[departement],b[departement],c[departement],d[departement],e[departement]],'Annee':['2016', '2017', '2018', '2019', '2020']})
    figure = plt.figure()
    b.plot.bar(x='Annee',rot=0, title=txt)
    return fig_to_html(figure)


def AvgPrice_MC_Commune(dataset,commune):    
    a=dataset["2016"].groupby(['Commune'])['Prix MC ST'].mean()
    b=dataset["2017"].groupby(['Commune'])['Prix MC ST'].mean()
    c=dataset["2018"].groupby(['Commune'])['Prix MC ST'].mean()
    d=dataset["2019"].groupby(['Commune'])['Prix MC ST'].mean()
    e=dataset["2020"].groupby(['Commune'])['Prix MC ST'].mean()
    
    b=pd.DataFrame({f'Prix moyen du MC à {commune} sur les 5 ans': [a[commune],b[commune],c[commune],d[commune],e[commune]],'Annee':['2016', '2017', '2018', '2019', '2020']})
    figure = plt.figure()
    b.plot.bar(x='Annee',rot=0, title=f"Prix moyen MC à {commune} de 2016 à 2020")
    return fig_to_html(figure)


def Avg_ValeurFonciere_NatureMutation(data_year_1, data_year_2, data_year_3):
    moy1 =  list(data_year_1.groupby("Nature mutation")["Valeur fonciere"].mean())
    moy2 =  list(data_year_2.groupby("Nature mutation")["Valeur fonciere"].mean())
    moy3 =  list(data_year_3.groupby("Nature mutation")["Valeur fonciere"].mean())
    moy = moy1+moy2+moy3
    gr = ["2016"]*6+["2018"]*6+["2020"]*6
    nm = list(data_year_1['Nature mutation'].unique())*3
    df = pd.DataFrame({'nature mutation':nm ,'valeur fonciere moyenne':moy,'annee':gr })
    fig = px.bar(df,x="valeur fonciere moyenne", y="nature mutation",text=moy, orientation='h',color="annee",barmode='group', height=600, width=1000)
    return fig.to_html()


### 5) Mutations per month (2 years comparaison)  ### (new)
def Mutations_TimeSeries(data_year_1, data_year_2):     
    d1 = data_year_1.copy()
    d2 = data_year_2.copy()
    d1.drop(d1[d1['Date mutation'] == 0].index, inplace = True)
    d2.drop(d2[d2['Date mutation'] == 0].index, inplace = True)
    d1['Date mutation']=pd.to_datetime(d1['Date mutation'], format='%d/%m/%Y')
    d2['Date mutation']=pd.to_datetime(d2['Date mutation'], format='%d/%m/%Y')

    d1['month'] = d1['Date mutation'].dt.strftime('%m')
    d2['month'] = d2['Date mutation'].dt.strftime('%m')
    count_1 =  list(d1["month"].value_counts())
    count_2 =  list(d2["month"].value_counts())
    
    c = count_1 + count_2
    ans = ["2020"]*12+["2016"]*12
    mois = list(d1['month'].unique())*2
    txt = "Evolution des mutations pendant l'année entre 2016 et 2020"
    df = pd.DataFrame({'month':mois ,'count':c,'annee':ans })
    fig = px.bar(df,x="month", y="count",text=c,color="annee",barmode='group', width=1000, height=600, title=txt)
    return fig.to_html()

dataCovid = pd.read_csv("data/covid data/dataCovid.csv", sep=";")
clean_dataCovid = data_cleaning(dataCovid, perc_NaN=20)
clean_dataCovid

def CasCovid_2020(data, year):   
    df = data.copy()
    df["Date mutation"]=pd.to_datetime(df["Date mutation"], format="%d/%m/%Y")
    df.drop(df[df['Date mutation'].dt.month == 8].index, inplace = True)
    df.drop(df[df['Date mutation'].dt.month == 9].index, inplace = True)
    df.drop(df[df['Date mutation'].dt.month == 10].index, inplace = True)
    df.drop(df[df['Date mutation'].dt.month == 11].index, inplace = True)
    df.drop(df[df['Date mutation'].dt.month == 12].index, inplace = True)
    c=  list(df["Date mutation"].value_counts())
    
    df['New cases']=clean_dataCovid['New cases']
    df['Date']=clean_dataCovid['Date']
    df["Date"]=pd.to_datetime(df["Date"], format="%d/%m/%Y")
    dbis = pd.DataFrame({'Date': df['Date'],'New cases':df['New cases'],'Date mutation':df['Date mutation'],'total':df['total']})

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=dbis['Date'], y=dbis['New cases'], name="nouveau cas de covid"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dbis['Date'], y=c, name="nombre de vente"),
        secondary_y=True,
    )
    fig.update_layout(title_text="title")
    fig.update_xaxes(title_text="date")
    fig.update_yaxes(title_text=" Nouveau cas covid", secondary_y=False)
    fig.update_yaxes(title_text=" nombre de transactions immobilières", secondary_y=True)
    return fig