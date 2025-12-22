# variants/services.py
import requests
def fetch_genebe_data(chrom, pos, ref, alt, genome_build='hg38'):
    """
    Genebe API'sine doğrudan bağlanarak veriyi çeker (Kütüphane kullanmaz).
    """
    # Genebe'nin halka açık API adresi
    api_url = "https://api.genebe.net/cloud/api-public/v1/annotate_variants"
    
    # Girdileri büyük harfe çevir ve string formatını hazırla
    ref = ref.upper()
    alt = alt.upper()
    variant_string = f"{chrom}-{pos}-{ref}-{alt}"
    
    print(f"--- API'ye Soruluyor: {variant_string} ---")

    try:
        # API'ye gidecek paket (Payload)
        payload = {
            "variants": [variant_string],
            "genome_build": genome_build
        }

        # İsteği gönder (POST Request)
        response = requests.post(api_url, json=payload, timeout=10)

        # Eğer sunucu hata verirse (Örn: 404, 500)
        if response.status_code != 200:
            return {'error': f"Sunucu Hatası: {response.status_code}"}

        # Gelen JSON verisini al
        json_data = response.json()
        
        # Veri boş mu kontrol et (Bazen API boş liste döner)
        if not json_data or len(json_data) == 0:
             return {'error': 'Varyant veritabanında bulunamadı.'}

        # İlk varyantı al
        data = json_data[0]

        # *** HATA AYIKLAMA İÇİN TERMİNALE BASALIM ***
        # Bu sayede hangi verilerin geldiğini görebileceksin
        print("GELEN HAM VERİ:", data.keys())

        # Sonuç sözlüğünü oluştur (Güvenli .get metodu ile)
        result = {
            'chrom': chrom,
            'pos': pos,
            'revel_score': data.get('revel_score', '-'),
            'cadd_phred': data.get('cadd_phred', '-'),
            'phylop': data.get('phylop100way_vertebrate', '-'),
            'message': 'Başarılı'
        }

        # Consequence verisini güvenli şekilde çekmeye çalışalım
        # API bazen 'consequences' bazen başka isimler kullanabilir, ham veriyi string yapıp alalım
        if 'consequences' in data and data['consequences']:
            # Bazen liste içinde sözlük döner, ilkini alıp gene/etkiyi yazdıralım
            cons_list = data['consequences']
            if isinstance(cons_list, list) and len(cons_list) > 0:
                # İlk etkinin adını al (Örn: missense_variant)
                result['consequence'] = cons_list[0].get('consequence', 'Bilinmiyor')
            else:
                result['consequence'] = str(cons_list)
        else:
             result['consequence'] = 'Belirtilmemiş'

        return result

    except requests.exceptions.RequestException as e:
        return {'error': f"Bağlantı Hatası: {str(e)}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f"Beklenmedik Hata: {str(e)}"}