from django import forms

class VariantSearchForm(forms.Form):
    # Chromosome list: 1-22 + X, Y
    CHROMOSOME_CHOICES = [
        (str(i), f'Chromosome {i}') for i in range(1, 23)
    ] + [('X', 'Chromosome X'), ('Y', 'Chromosome Y'), ('M', 'Chromosome M')] 

    chromosome = forms.ChoiceField(
        choices=CHROMOSOME_CHOICES, 
        label="Chromosome",
        initial='17' 
    )
    
    position = forms.IntegerField(
        label="Position (hg38)", 
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 43044295'})
    )
    
    # REFERENCE (Ref) Input
    ref = forms.CharField(
        label="Reference (Ref)", 
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: G',
            'pattern': '[ATGCatgc]+',                       # Sadece bu harflere izin ver
            'title': 'Enter DNA bases (A, T, G, C) only',   # Hover (İpucu) mesajı
            'oninput': "this.value = this.value.toUpperCase()" # Otomatik BÜYÜK harf
        })
    )
    
    # ALTERNATE (Alt) Input
    alt = forms.CharField(
        label="Alternate (Alt)", 
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: A',
            'pattern': '[ATGCatgc]+',                       # Sadece bu harflere izin ver
            'title': 'Enter DNA bases (A, T, G, C) only',   # Hover (İpucu) mesajı
            'oninput': "this.value = this.value.toUpperCase()" # Otomatik BÜYÜK harf
        })
    )