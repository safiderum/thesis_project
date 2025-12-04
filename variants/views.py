from django.shortcuts import render
from .forms import VariantSearchForm

def search_variant(request):
    results = None  # Başlangıçta sonuç yok

    if request.method == 'POST':
        form = VariantSearchForm(request.POST)
        if form.is_valid():
            # temporary mock data 
            cd = form.cleaned_data 
            
            results = {
                'chrom': cd['chromosome'],
                'pos': cd['position'],
                'revel_score': 0.85,   # mock scrore
                'cadd_phred': 24.5,    # mock score
                'message': 'Genebe bağlantısı henüz yapılmadı, bu test verisidir.'
            }
    else: # empty page at first
        form = VariantSearchForm()

    return render(request, 'variants/home.html', {'form': form, 'results': results})