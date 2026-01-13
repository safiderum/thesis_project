from django.shortcuts import render
import requests
from .forms import VariantSearchForm  

def search_variant(request):
    context = {}
    
    if request.method == "POST":
        form = VariantSearchForm(request.POST)
        
        if form.is_valid():
            # Form 
            chromosome = form.cleaned_data.get("chromosome", "")
            position = form.cleaned_data.get("position", "")
            ref = form.cleaned_data.get("ref", "")
            alt = form.cleaned_data.get("alt", "")

            # API 
            chrom_clean = str(chromosome).replace("chr", "").replace("Chr", "").strip()
            url = "https://api.genebe.net/cloud/api-public/v1/variant"
            
            params = {
                "chr": chrom_clean,
                "pos": position,
                "ref": ref,
                "alt": alt,
                "genome": "hg38"
            }

            try:
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    raw_data = response.json()
                    variants_list = raw_data.get("variants", [])
                    
                    if variants_list:
                        variant_data = variants_list[0]
                        
                        # Transkript 
                        consequences = variant_data.get("consequences", [])
                        selected_cons = {}
                        for cons in consequences:
                            if cons.get("canonical") is True:
                                selected_cons = cons
                                break
                        if not selected_cons and consequences:
                            selected_cons = consequences[0]

                        # genel
                        variant_effect_raw = variant_data.get("effect", "-")
                        variant_info = {
                            "gene_symbol": variant_data.get("gene_symbol", "-"),
                            "effect": variant_effect_raw.replace("_", " ").title(),
                            "hgvs_c": selected_cons.get("hgvs_c", "-"),
                            "hgvs_p": selected_cons.get("hgvs_p", "-"),
                            "transcript": selected_cons.get("transcript", "-"),
                            "acmg_class": variant_data.get("acmg_classification", "-"),
                            "clinvar_class": variant_data.get("clinvar_classification", "-")
                        }

                        # PHYLOP 
                        raw_phylop = variant_data.get("phylop100way_score", None)
                        phylop_analysis = None
                        
                        if raw_phylop is not None:
                            try:
                                p_score = float(raw_phylop)
                                if p_score > 4.0:
                                    phylop_analysis = {"score": p_score, "interpretation": "Extreme Evolutionary Constraint", "comment": "Invariant across vertebrates. Mutation likely incompatible with survival.", "significance": "Highly Conserved", "color": "bg-purple"}
                                elif 1.6 <= p_score <= 4.0:
                                    phylop_analysis = {"score": p_score, "interpretation": "Significant Conservation", "comment": "Evidence of purifying selection. Important functional role.", "significance": "Conserved", "color": "bg-red"}
                                elif -1.5 <= p_score < 1.6:
                                    phylop_analysis = {"score": p_score, "interpretation": "Neutral Evolution", "comment": "Consistent with background mutation rate. Likely tolerated.", "significance": "Neutral", "color": "bg-gray"}
                                else:
                                    phylop_analysis = {"score": p_score, "interpretation": "Accelerated Evolution", "comment": "Changing faster than expected (Positive selection).", "significance": "Accelerated", "color": "bg-orange"}
                            except ValueError:
                                phylop_analysis = None

                        # MITOTIP
                        raw_mitotip = variant_data.get("mitotip_score", None)
                        mitotip_pred = "-" 
                        if raw_mitotip is not None:
                            try:
                                m_score = float(raw_mitotip)
                                if m_score > 16.25: mitotip_pred = "Likely Pathogenic"
                                elif m_score >= 12.66: mitotip_pred = "Possibly Pathogenic"
                                elif m_score >= 8.44: mitotip_pred = "Possibly Benign"
                                else: mitotip_pred = "Likely Benign"
                            except ValueError:
                                mitotip_pred = variant_data.get("mitotip_prediction", "-")
                        
                        # --- 4. TÜM ARAÇLARI HAZIRLA (HAVUZ) ---
                        # Önce hepsini bir havuza atıyoruz, sonra sıralayacağız.
                        tools_pool = {
                            "AlphaMissense": { "score": variant_data.get("alphamissense_score", "-"), "pred": variant_data.get("alphamissense_prediction", "-") },
                            "REVEL": { "score": variant_data.get("revel_score", "-"), "pred": variant_data.get("revel_prediction", "-") },
                            "BayesDel": { "score": variant_data.get("bayesdelnoaf_score", "-"), "pred": variant_data.get("bayesdelnoaf_prediction", "-") },
                            "SpliceAI": { "score": variant_data.get("spliceai_max_score", "-"), "pred": variant_data.get("spliceai_max_prediction", "-") },
                            "dbscSNV ADA": { "score": variant_data.get("dbscsnv_ada_score", "-"), "pred": variant_data.get("dbscsnv_ada_prediction", "-") },
                            "MitoTip": { "score": raw_mitotip if raw_mitotip else "-", "pred": mitotip_pred }
                        }

                        # --- 5. DİNAMİK SIRALAMA MANTIĞI (YENİ) ---
                        final_predictions = {}
                        order_keys = []

                        # Mito
                        if chrom_clean == "M" or chrom_clean == "MT":
                            order_keys = ["MitoTip", "BayesDel", "REVEL", "AlphaMissense", "SpliceAI", "dbscSNV ADA"]
                        
                        # Splice
                        elif "splice" in variant_effect_raw.lower():
                            order_keys = ["SpliceAI", "dbscSNV ADA", "BayesDel", "REVEL", "AlphaMissense", "MitoTip"]
                        
                        # non-codin non splice
                        elif "utr" in variant_effect_raw.lower() and "splice" not in variant_effect_raw.lower():
                            order_keys = ["BayesDel", "SpliceAI", "REVEL", "AlphaMissense", "dbscSNV ADA", "MitoTip"]
                        
                        else:
                            order_keys = ["AlphaMissense", "REVEL", "BayesDel", "SpliceAI", "dbscSNV ADA", "MitoTip"]

                        # Belirlenen sıraya göre sözlüğü oluştur
                        for key in order_keys:
                            final_predictions[key] = tools_pool[key]

                        context["variant_info"] = variant_info
                        context["predictions"] = final_predictions # Sıralanmış liste gidiyor
                        context["phylop_analysis"] = phylop_analysis
                        
                    else:
                        context["error"] = "No variants found in the database."

                elif response.status_code == 404:
                    context["error"] = "Variant not found (404)."
                else:
                    context["error"] = f"API Error: {response.status_code}"

            except Exception as e:
                print(f"Error: {e}")
                context["error"] = "An error occurred while connecting to the API."
            
    else:
        form = VariantSearchForm()

    context["form"] = form
    return render(request, "variants/home.html", context)