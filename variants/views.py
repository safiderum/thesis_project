from django.shortcuts import render
import requests
from .forms import VariantSearchForm  

def search_variant(request):
    context = {}
    
    # 1. Formu Yönetme (GET veya POST isteği)
    if request.method == "POST":
        form = VariantSearchForm(request.POST)
        
        if form.is_valid():
            # Verileri formdan güvenli bir şekilde alıyoruz
            # Not: cleaned_data içindeki anahtarlar forms.py'daki değişken isimleriyle aynı olmalı
            chromosome = form.cleaned_data.get("chromosome", "")
            position = form.cleaned_data.get("position", "")
            ref = form.cleaned_data.get("ref", "")
            alt = form.cleaned_data.get("alt", "")

            # --- API Mantığı Başlangıcı ---
            
            # Kromozom temizliği (chr17 -> 17)
            # Eğer chromosome bir sayı değil string geliyorsa str() içine alın
            chrom_clean = str(chromosome).replace("chr", "").replace("Chr", "").strip()

            url = "https://api.genebe.net/cloud/api-public/v1/variant"
            
            params = {
                "chr": chrom_clean,
                "pos": position,
                "ref": ref,
                "alt": alt,
                "genome": "hg38"
            }

            print(f"--- API'ye Soruluyor: {url} | Parametreler: {params} ---")

            try:
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    context["result"] = data
                elif response.status_code == 404:
                    context["error"] = "Varyant bulunamadı (404). Koordinatları kontrol edin (hg38)."
                else:
                    context["error"] = f"API Hatası: {response.status_code}"

            except Exception as e:
                print(f"Bağlantı Hatası: {e}")
                context["error"] = "API bağlantı hatası."
            
            # --- API Mantığı Sonu ---
            
    else:
        # Sayfa ilk açıldığında boş form göster
        form = VariantSearchForm()

    # Formu context'e ekliyoruz ki HTML'de {{ form }} çalışsın
    context["form"] = form

    return render(request, "variants/home.html", context)