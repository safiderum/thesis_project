from django import forms

class VariantSearchForm(forms.Form):
    CHROMOSOME_CHOICES = [
        ('chr1', 'Chromosome 1'),
        ('chr2', 'Chromosome 2'),
        ('chr3', 'Chromosome 3'),
        ('chrX', 'Chromosome X'),
        ('chrY', 'Chromosome Y'),
    ]

    chromosome = forms.ChoiceField(choices=CHROMOSOME_CHOICES, label="Chromosome")
    position = forms.IntegerField(min_value=1, label="Position")
    ref = forms.CharField(max_length=20, label="Reference (Ref)")
    alt = forms.CharField(max_length=20, label="Alternate (Alt)")