from django import forms


class MoveForm(forms.Form):

    new_state = forms.IntegerField()

    price = forms.FloatField()

    date_adquired = forms.CharField()
    date_started = forms.CharField()
    date_other = forms.CharField()

    time_played = forms.FloatField()
    time_other = forms.FloatField()

    playstyle = forms.IntegerField()