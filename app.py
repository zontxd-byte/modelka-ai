import os
import streamlit as st
import replicate

st.set_page_config(page_title="Generator Modelki AI", page_icon="📸")

st.title("📸 Generator Realistycznej Modelki AI")
st.write("Wybierz styl, a model stworzy fotorealistyczną postać.")

REPLICATE_KEY = st.secrets.get("REPLICATE_API_TOKEN", os.environ.get("REPLICATE_API_TOKEN", ""))

if not REPLICATE_KEY:
    st.error("⚠️ Brak klucza REPLICATE_API_TOKEN w Secrets na Streamlit Cloud!")
    st.stop()

client = replicate.Client(api_token=REPLICATE_KEY)

stylowe_ubrania = [
    "brak ubrań",
    "koronkowe czerwone body"
    "czarna skórzana kurtka i dżinsy",
    "elegancka jedwabna suknia wieczorowa",
    "casualowy, lniany garnitur w odcieniu beżu",
    "street style: oversized hoodie, białe sneakersy",
    "letni crop top, szorty z wysokim stanem",
    "klasyczna, biała koszula z podwiniętymi rękawami"
]

tla_sesji = [
    "ulice tętniącego życiem miasta w Tokio",
    "minimalistyczne, jasne studio fotograficzne",
    "kawiarnia na świeżym powietrzu w Paryżu",
    "industrialny loft z czerwonej cegły",
    "klify i ocean o wschodzie słońca",
    "nowoczesne, szklane biuro w Nowym Jorku"
]

fryzury = [
    "długie, falowane blond włosy",
    "krótkie, asymetryczne ciemne włosy",
    "rude, proste włosy do ramion",
    "wysoki kucyk"
]

col1, col2, col3 = st.columns(3)
with col1:
    ubranie = st.selectbox("Styl ubioru:", stylowe_ubrania, index=0)
with col2:
    tlo = st.selectbox("Tło:", tla_sesji, index=0)
with col3:
    fryzura = st.selectbox("Fryzura:", fryzury, index=0)

if st.button("🌟 GENERUJ MODELKĘ"):
    final_prompt = (
        f"Hyperrealistic portrait photo of a professional European fashion model. "
        f"She is wearing {ubranie}. Her hair is styled in {fryzura}. "
        f"She is standing in {tlo}. High resolution, 8k, shot on a Canon EOS R5, 35mm lens, "
        f"natural makeup, authentic look, professional lighting, fine details."
    )

    with st.spinner("Generuję obraz... (ok. 15 sekund)"):
        try:
            output = client.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": final_prompt,
                    "aspect_ratio": "9:16",
                    "output_format": "jpg",
                    "output_quality": 95
                }
            )
            
            # Pobieramy bajty ze zwróconego strumienia pliku
            if hasattr(output, "read"):
                image_data = output.read()
            elif isinstance(output, list) and len(output) > 0:
                image_data = output[0]
            else:
                image_data = str(output)

            st.success("Wygenerowano!")
            st.image(image_data, caption="Modelka AI", use_container_width=True)
        except Exception as e:
            st.error(f"Błąd: {e}")
