from django.shortcuts import render
import requests
# DÜZELTME: forms.py dosyanızdaki doğru sınıf ismini import ediyoruz
from .forms import VariantSearchForm  

def search_variant(request):
    context = {}
    
    if request.method == "POST":
        # DÜZELTME: Doğru form sınıfını kullanıyoruz
        form = VariantSearchForm(request.POST)
        
        if form.is_valid():
            chromosome = form.cleaned_data.get("chromosome", "")
            position = form.cleaned_data.get("position", "")
            ref = form.cleaned_data.get("ref", "")
            alt = form.cleaned_data.get("alt", "")

            # API Ayarları
            # Kromozom verisinden 'chr' önekini temizliyoruz (API sadece numara istiyor olabilir)
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
                    raw_data = response.json()
                    
                    # --- JSON PARSING ---
                    
                    # Veri 'variants' listesinin içinde geliyor
                    variants_list = raw_data.get("variants", [])
                    
                    if variants_list:
                        # İlk varyantı al
                        variant_data = variants_list[0]
                        
                        consequences = variant_data.get("consequences", [])
                        selected_cons = {}
                        
                        # Önce canonical olan
                        for cons in consequences:
                            if cons.get("canonical") is True:
                                selected_cons = cons
                                break
                        
                        # Eğer canonical yoksa listenin ilk elemanı
                        if not selected_cons and consequences:
                            selected_cons = consequences[0]

                        # 1. Genel Bilgiler Sözlüğü
                        variant_info = {
                            "gene_symbol": variant_data.get("gene_symbol", "-"),
                            "effect": variant_data.get("effect", "-").replace("_", " ").title(), # Örn: Missense Variant
                            "hgvs_c": selected_cons.get("hgvs_c", "-"),
                            "hgvs_p": selected_cons.get("hgvs_p", "-"),
                            "transcript": selected_cons.get("transcript", "-"),
                            "acmg_class": variant_data.get("acmg_classification", "-"), # Pathogenic
                            "clinvar_class": variant_data.get("clinvar_classification", "-")
                        }

                        # 2. Skorlar Sözlüğü 
                        predictions = {
                            "REVEL": {
                                "score": variant_data.get("revel_score", "-"),
                                "pred": variant_data.get("revel_prediction", "-")
                            },
                            "AlphaMissense": {
                                "score": variant_data.get("alphamissense_score", "-"),
                                "pred": variant_data.get("alphamissense_prediction", "-")
                            },
                            "BayesDel": {
                                "score": variant_data.get("bayesdelnoaf_score", "-"),
                                "pred": variant_data.get("bayesdelnoaf_prediction", "-")
                            },
                            "PhyloP (100way)": {
                                "score": variant_data.get("phylop100way_score", "-"),
                                "pred": variant_data.get("phylop100way_prediction", "-")
                            },
                             "SpliceAI": {
                                "score": variant_data.get("spliceai_max_score", "-"),
                                "pred": variant_data.get("spliceai_max_prediction", "-")
                            }
                        }

                        context["variant_info"] = variant_info
                        context["predictions"] = predictions
                        
                    else:
                        context["error"] = "API boş sonuç döndürdü (Varyant bulunamadı)."

                elif response.status_code == 404:
                    context["error"] = "Varyant veritabanında bulunamadı (404)."
                else:
                    context["error"] = f"API Hatası: {response.status_code}"

            except Exception as e:
                print(f"Hata detayı: {e}")
                context["error"] = "Bağlantı sırasında bir hata oluştu."
            
    else:
        form = VariantSearchForm()

    context["form"] = form
    return render(request, "variants/home.html", context)