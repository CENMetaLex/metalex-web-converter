'''
Created on 24 May 2011

@author: hoekstra
'''


from django import forms
from datetime import date

class QueryForm(forms.Form):
    title = forms.CharField(max_length = 150, required=True)
    date = forms.DateField(initial= date.today,required=True)
    
