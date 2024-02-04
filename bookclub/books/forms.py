from django import forms

class BookRatingForm(forms.Form):
    rating = forms.IntegerField(label="Rating", widget=forms.TextInput(attrs={'class':'text-input'}))
    readDate = forms.DateField(label="Date Read", widget=forms.DateInput(attrs={'type':'date', 'class':'date-input'}))
