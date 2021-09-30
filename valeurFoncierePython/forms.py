from django import forms
from valeurFoncierePython.graphics import clean_datasets
import pandas as pd

#Forms servant à savoir quel département on veut voir
class DepartementForm(forms.Form):
    departement = forms.CharField(required=True)

class CommuneForm(forms.Form):
    commune = forms.CharField(required=True)

    