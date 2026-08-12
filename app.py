import os
import time
import streamlit as st
import replicate

st.set_page_config(page_title="Studio Modelki AI 3D & Video", page_icon="🎬", layout="centered")

st.title("🎬 Profesjonalne Studio Modelki AI")
st.write("Generuj fotorealistyczne sesje zdjęciowe oraz animacje wideo w ruchu.")

# Pobieranie klucza API z ustawień Streamlit
REPLICATE_KEY = st.secrets.get("REPLICATE_API_TOKEN", os.environ.get("REPLICATE_API_TOKEN", ""))

if not REPLICATE_KEY:
    st.error("⚠️ Brak klucza REPLICATE_API_TOKEN w Secrets na Streamlit Cloud!")
    st.stop()

client = replicate.Client(api_token=REPLICATE_KEY)

# --- SŁOWNIKI KONFIGURACYJNE ---
ubrania_dict = {
    "Czarny koronkowy body": "black lace bodysuit with delicate sheer accents",
    "Biały elegancki komplet bielizny": "white silk and lace lingerie set",
    "Czerwony satynowy gorset": "red satin corset with black lace trim",
    "Casual: Skórzana kurtka i dżinsy": "stylish black leather jacket and dark fitted jeans",
    "Letni crop top i szorty": "summer crop top, high-waisted denim shorts",
    "Elegancka jedwabna suknia": "luxurious floor-length silk evening gown"
}

pozy_dict = {
    "Kucanie": "squatting down low, dynamic fashionable pose",
    "Klęczenie": "kneeling gracefully on the floor, polished posture",
    "Siedzenie z podkurczonymi nogami": "sitting on the floor with knees pulled close",
    "Na stojąco (pełna sylwetka)": "standing full body pose, elegant posture",
    "Oparta o ścianę": "leaning relaxed against a textured wall"
}

tla_dict = {
    "Luksusowa sypialnia": "modern luxury bedroom, soft warm ambient lighting, plush velvet accents",
    "Jasne studio (minimalizm)": "bright minimalist photo studio, clean background, soft daylight",
    "Industrialny loft": "industrial loft apartment, exposed brick wall, warm floor lamps",
    "Plaża o zachodzie słońca": "sandy beach at sunset, warm golden hour lighting",
    "Nowoczesny apartament z widokiem": "modern penthouse interior, panoramic city window view at night"
}

fryzury_dict = {
    "Długie falowane blond": "long wavy blonde hair falling naturally over shoulders",
    "Ciemny elegancki bob": "dark brunette sleek bob hairstyle",
    "Rude proste": "straight shoulder-length ginger hair",
    "Wysoki upięty kucyk": "high sleek ponytail"
}

kadry_dict = {
    "Pełna sylwetka (Full Body)": "full body shot, feet to head framing",
    "Plan średni (Medium Shot)": "three-quarter shot, knee-up framing",
    "Bliski kadr / Portret": "close-up portrait shot focusing on face and shoulders"
}

ruchy_vimeo_dict = {
    "Brak (Tylko zdjęcie)": None,
    "Płynny ruch i zmiana pozy": "model slowly shifts pose, gentle body motion, subtle gaze towards camera",
    "Przeczesanie włosów": "model gently runs fingers through hair in slow motion, natural motion",
    "Lekki obrót i uśmiech": "camera slow pan around the model, subtle natural smile"
}

# --- FORMULARZ WYBORU ---
st.subheader("1. Skonfiguruj wygląd i pozę")
col1, col2 = st.columns(2)

with col1:
    ubranie_label = st.selectbox("Strój / Bielizna:", list(ubrania_dict.keys()))
    poza_label = st.selectbox("Poza modelki:", list(pozy_dict.keys()))
    kadr_label = st.selectbox("Kadr / Ujęcie:", list(kadry_dict.keys()))

with col2:
    tlo_label = st.selectbox("Tło / Otoczenie:", list(tla_dict.keys()))
    fryzura_label = st.selectbox("Fryzura:", list(fryzury_dict.keys()))
    ruch_label = st.selectbox("Animacja / Ruch (Wideo):", list(ruchy_vimeo_dict.keys()))

st.markdown("---")

if st.button("🌟 GENERUJ SESJĘ / WIDEO", use_container_width=True):
    ubranie_en = ubrania_dict[ubranie_label]
    poza_en = pozy_dict[poza_label]
    tlo_en = tla_dict[tlo_label]
    fryzura_en = fryzury_dict[fryzura_label]
    kadr_en = kadry_dict[kadr_label]
    ruch_prompt = ruchy_vimeo_dict[ruch_label]

    final_photo_prompt = (
        f"A hyperrealistic fashion photograph, {kadr_en}. "
        f"An attractive European female model wearing a {ubranie_en}. "
        f"She is {poza_en}. Her hair is {fryzura_en}. "
        f"Set in {tlo_en}. Shot on Hasselblad H6D-100c, 85mm lens, f/2.0 aperture, "
        f"soft natural shadow distribution, sharp eyes, natural skin texture with fine details, "
        f"high resolution, 8k, editorial fashion style."
    )

    with st.spinner("Generuję zdjęcie bazowe FLUX 1.1 Pro... (ok. 15 sekund)"):
        try:
            # Step 1: Generowanie zdjęcia bazowego
            photo_output = client.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": final_photo_prompt,
                    "aspect_ratio": "9:16",
                    "output_format": "jpg",
                    "output_quality": 98
                }
            )

            # Pobranie bajtów lub URL
            if hasattr(photo_output, "read"):
                image_data = photo_output.read()
            elif isinstance(photo_output, list) and len(photo_output) > 0:
                image_data = photo_output[0]
            else:
                image_data = str(photo_output)

            st.success("Wygenerowano zdjęcie bazowe!")
            st.image(image_data, caption=f"{ubranie_label} - {poza_label}", use_container_width=True)

            # Step 2: Generowanie wideo (jeśli wybrano ruch)
            if ruch_prompt:
                st.markdown("---")
                st.subheader("🎬 Tworzenie animacji wideo...")
                
                with st.spinner("Generowanie wideo AI na podstawie zdjęcia... (to może zająć 1-2 minuty)"):
                    # Konwersja obrazu na URL do przekazania modelowi wideo
                    image_url = photo_output if isinstance(photo_output, str) else str(photo_output)
                    
                    video_output = client.run(
                        "stability-ai/stable-video-diffusion:3f0457e4619da3c000508771000f484bba573da4e0ed40787012bc133bc02d4e",
                        input={
                            "input_image": image_url,
                            "motion_bucket_id": 127,
                            "fps": 6,
                            "cond_aug": 0.02
                        }
                    )

                    st.success("Wygenerowano animację wideo!")
                    st.video(video_output)

        except Exception as e:
            st.error(f"Błąd podczas generowania: {e}")
