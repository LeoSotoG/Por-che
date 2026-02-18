import os
import streamlit as st
from openai import OpenAI
from prompts import stronger_prompt
from PIL import Image
import datetime
import numpy as np
import pandas as pd
import pickle   
import joblib


# ----------------------------
# CONFIGURACIÓN DE PÁGINA
# ----------------------------
st.set_page_config(layout="wide")

@st.cache_resource
def load_model():
    data = joblib.load("modelo_porsche_0.joblib")
    return data["model"], data["scaler"], data["columns"]

model, scaler, columns = load_model()


# ----------------------------
# CARGA DE VARIABLES DE ENTORNO
# ----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# ----------------------------
# CSS PERSONALIZADO
# ----------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #000000;
    color: white;
}
.neon-text {
    color: #00f0ff;
    text-shadow: 0 0 5px #00f0ff,
                 0 0 10px #00f0ff,
                 0 0 20px #00f0ff;
    font-weight: bold;
    font-size: 24px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LAYOUT DE 2 COLUMNAS
# ----------------------------
col1, col2 = st.columns([1, 1])

# ============================
# IZQUIERDA: CHAT
# ============================
with col1:
    st.markdown('<p class="neon-text">Chat Porsche Intelligence</p>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "¿Qué modelo Porsche quieres analizar?"}
        ]

    # Mostrar todo el historial de chat
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        conversation = [{"role": "system", "content": stronger_prompt}]
        conversation += st.session_state.messages

        # Respuesta del asistente
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=MODEL,
                messages=conversation,
                stream=True
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

with col2:

    # ======================
    # LOGO
    # ======================
    if os.path.exists("Logo.png"):
        logo = Image.open("Logo.png")
        st.image(logo, width=450)
    else:
        st.warning("Logo.png no se encontró.")

    st.markdown("---")

    st.subheader("📊 Calculadora de Precio")

    current_year = datetime.datetime.now().year

    # ======================
    # DATOS BÁSICOS (CON LÍMITES REALES)
    # ======================

    mileage_km = st.number_input(
        "Kilometraje (km)",
        min_value=0.0,
        max_value=510000.00,
        value=101001.0
    )

    power_hp = st.number_input(
        "Potencia (HP)",
        min_value=50.0,
        max_value=7190.0,
        value=901.0
    )

    weight_kg = st.number_input(
        "Peso (kg)",
        min_value=800.0,
        max_value=23000.0,
        value=1600.0
    )

    cylinders = st.number_input(
        "Número de cilindros",
        min_value=0,
        max_value=10,
        value=6,
        step=1
    )

    cylinders_volume_cc = st.number_input(
        "Cilindrada (cc)",
        min_value=0.0,
        max_value=28940.0,
        value=3000.0
    )

    nr_seats = st.number_input(
        "Número de asientos",
        min_value=1,
        max_value=6,
        value=2,
        step=1
    )

    nr_doors = st.number_input(
        "Número de puertas",
        min_value=1,
        max_value=6,
        value=3,
        step=1
    )

    electric_range_km = st.number_input(
        "Autonomía eléctrica (km)",
        min_value=0.0,
        max_value=811.0,
        value=0.0
    )

    equipment_total = st.number_input(
        "Total equipamiento",
        min_value=0,
        max_value=200,
        value=20
    )

    # ======================
    # AÑO
    # ======================

    registration_year = st.number_input(
        "Año de registro",
        min_value=1950,
        max_value=current_year,
        value=2018,
        step=1
    )

    vehicle_age = max(current_year - registration_year, 0)

    # ======================
    # VALIDACIONES INTELIGENTES
    # ======================

    warnings = []

    if mileage_km > 100000:
        warnings.append("⚠️ Kilometraje alto")

    if power_hp > 800:
        warnings.append("⚠️ Potencia muy elevada")

    if weight_kg < 900:
        warnings.append("⚠️ Peso inusualmente bajo")

    if cylinders == 0 and cylinders_volume_cc > 0:
        warnings.append("⚠️ Cilindrada sin cilindros definidos")

    if vehicle_age > 50:
        warnings.append("⚠️ Vehículo clásico muy antiguo")

    if warnings:
        st.warning(" | ".join(warnings))

    # ======================
    # BOOLEANOS
    # ======================

    has_particle_filter = st.checkbox("Filtro de partículas.")
    is_used = st.checkbox("Vehículo usado.")
    has_full_service_history = st.checkbox("Historial completo de Servicios.")
    non_smoking = st.checkbox("El dueño No es fumador")
    seller_is_dealer = st.checkbox("Vendedor es de concesionario")
    seller_type_PrivateSeller = st.checkbox("Vendedor privado")

    # ======================
    # BODY TYPE
    # ======================

    body_type = st.selectbox(
        "Tipo de carrocería",
        ["Convertible", "Coupe", "Off-Road/Pick-up", "Sedan",
         "Station wagon", "Van", "Other"]
    )

    # ======================
    # TRANSMISIÓN
    # ======================

    transmission = st.selectbox(
        "Transmisión",
        ["Automatic", "Manual", "Semi-automatic"]
    )

    # ======================
    # TRACCIÓN
    # ======================

    drive_train = st.selectbox(
        "Tracción",
        ["AWD", "Front Wheel Drive", "Rear Wheel Drive"]
    )

    # ======================
    # COMBUSTIBLE
    # ======================

    fuel_category = st.selectbox(
        "Tipo de combustible",
        ["Gasoline", "Electric", "Electric/Gasoline",
         "Electric/Diesel", "Ethanol", "LPG", "Others"]
    )

    # ======================
    # PAÍS
    # ======================

    country = st.selectbox(
        "País",
        ["DE", "ES", "FR", "IT", "NL", "BE", "LU"]
    )

    data = joblib.load("modelo_porsche_0.joblib")
    model = data["model"]
    scaler = data["scaler"]
    columns = data["columns"]


    # ======================
    # BOTÓN
    # ======================

    if st.button("🚀 Calcular Precio Estimado"):

        km_per_year = mileage_km / (vehicle_age + 1)
        power_to_weight = power_hp / weight_kg if weight_kg > 0 else 0
        log_mileage = np.log1p(mileage_km)

        input_data = pd.DataFrame([{
            "mileage_km": mileage_km,
            "nr_seats": nr_seats,
            "nr_doors": nr_doors,
            "power_hp": power_hp,
            "cylinders": cylinders,
            "cylinders_volume_cc": cylinders_volume_cc,
            "weight_kg": weight_kg,
            "has_particle_filter": int(has_particle_filter),
            "electric_range_km": electric_range_km,
            "is_used": int(is_used),
            "has_full_service_history": int(has_full_service_history),
            "non_smoking": int(non_smoking),
            "seller_is_dealer": int(seller_is_dealer),
            "vehicle_age": vehicle_age,

            "body_type_Convertible": 1 if body_type == "Convertible" else 0,
            "body_type_Coupe": 1 if body_type == "Coupe" else 0,
            "body_type_Off-Road/Pick-up": 1 if body_type == "Off-Road/Pick-up" else 0,
            "body_type_Other": 1 if body_type == "Other" else 0,
            "body_type_Sedan": 1 if body_type == "Sedan" else 0,
            "body_type_Station wagon": 1 if body_type == "Station wagon" else 0,
            "body_type_Van": 1 if body_type == "Van" else 0,

            "transmission_Manual": 1 if transmission == "Manual" else 0,
            "transmission_Semi-automatic": 1 if transmission == "Semi-automatic" else 0,

            "drive_train_Front Wheel Drive": 1 if drive_train == "Front Wheel Drive" else 0,
            "drive_train_Rear Wheel Drive": 1 if drive_train == "Rear Wheel Drive" else 0,

            "fuel_category_Electric": 1 if fuel_category == "Electric" else 0,
            "fuel_category_Electric/Diesel": 1 if fuel_category == "Electric/Diesel" else 0,
            "fuel_category_Electric/Gasoline": 1 if fuel_category == "Electric/Gasoline" else 0,
            "fuel_category_Ethanol": 1 if fuel_category == "Ethanol" else 0,
            "fuel_category_Gasoline": 1 if fuel_category == "Gasoline" else 0,
            "fuel_category_LPG": 1 if fuel_category == "LPG" else 0,
            "fuel_category_Others": 1 if fuel_category == "Others" else 0,

            "country_code_BE": 1 if country == "BE" else 0,
            "country_code_DE": 1 if country == "DE" else 0,
            "country_code_ES": 1 if country == "ES" else 0,
            "country_code_FR": 1 if country == "FR" else 0,
            "country_code_IT": 1 if country == "IT" else 0,
            "country_code_LU": 1 if country == "LU" else 0,
            "country_code_NL": 1 if country == "NL" else 0,

            "seller_type_PrivateSeller": int(seller_type_PrivateSeller),

            "km_per_year": km_per_year,
            "power_to_weight": power_to_weight,
            "equipment_total": equipment_total,
            "log_mileage": log_mileage
        }])

        # 🔥 ORDENAR COLUMNAS
        input_data = input_data.reindex(columns=columns, fill_value=0)

        # 🔥 ESCALAR
        input_scaled = scaler.transform(input_data)

        # 🔥 PREDECIR
        prediction = model.predict(input_scaled)[0]

        st.success(f"💰 Precio estimado: € {prediction:,.0f}")

    
    # -----------------------------------
    # BOTÓN MARKETPLACES
    # -----------------------------------

    if st.button("🏎️ Ver Marketplaces de Lujo en Europa"):

        st.markdown("## 🌍 Compra Autos de Lujo en Europa")

        colA, colB = st.columns(2)

        with colA:
            st.subheader("🇩🇪 Mobile.de")
            st.write("El marketplace más grande de Alemania.")
            st.link_button("Visitar", "https://www.mobile.de")

            st.subheader("🇫🇷 JamesEdition")
            st.write("Marketplace exclusivo de lujo.")
            st.link_button("Visitar", "https://www.jamesedition.com")

            st.subheader("🇬🇧 PistonHeads")
            st.write("Comunidad británica de autos deportivos.")
            st.link_button("Visitar", "https://www.pistonheads.com")

        with colB:
            st.subheader("🇩🇪 AutoScout24")
            st.write("Plataforma líder en Europa.")
            st.link_button("Visitar", "https://www.autoscout24.com")

            st.subheader("🇳🇱 Classic Driver")
            st.write("Especialistas en autos clásicos premium.")
            st.link_button("Visitar", "https://www.classicdriver.com")

        st.success("🚀 Encuentra tu próximo Porsche en Europa.")
