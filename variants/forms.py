# variants/forms.py
from django import forms

class VariantSearchForm(forms.Form):
    # Kromozom listesini 1'den 22'ye + X, Y, M olarak otomatik üretelim
    CHROMOSOME_CHOICES = [
        (f'chr{i}', f'Chromosome {i}') for i in range(1, 23)
    ] + [('chrX', 'Chromosome X'), ('chrY', 'Chromosome Y'), ('chrM', 'Mitochondrial')]

    chromosome = forms.ChoiceField(choices=CHROMOSOME_CHOICES, label="Chromosome")
    position = forms.IntegerField(min_value=1, label="Position")
    ref = forms.CharField(max_length=20, label="Reference (Ref)")
    alt = forms.CharField(max_length=20, label="Alternate (Alt)")