import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# File dei dati
data_file = "prodotti.json"

# Carica dati esistenti o inizializza lista vuota
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def trova_prodotto(codice, data):
    for prodotto in data:
        if codice == prodotto["codice_texture"] or codice in prodotto["colori"]:
            return prodotto
    return None

def filtra_prodotti(data, clean=None, spf=None, microplastiche=None, talco=None):
    risultati = data
    if clean is not None:
        risultati = [p for p in risultati if clean in p.get("clean", [])]
    if spf is not None:
        risultati = [p for p in risultati if bool(p.get("spf")) == spf]
    if microplastiche is not None:
        risultati = [p for p in risultati if p.get("microplastic_free") == microplastiche]
    if talco is not None:
        risultati = [p for p in risultati if p.get("talc_free") == talco]
    return risultati

def esporta_excel(lista_prodotti):
    df = pd.DataFrame(lista_prodotti)
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

def esporta_pdf(prodotto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for key, value in prodotto.items():
        if isinstance(value, list):
            value = ', '.join(value)
        pdf.multi_cell(0, 10, f"{key}: {value}")
    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

st.sidebar.title("Navigazione")
pagina = st.sidebar.radio("Vai a:", ["Scheda prodotto", "Filtra prodotti", "Aggiungi prodotto"])

prodotti = load_data()

if pagina == "Aggiungi prodotto":
    st.title("➕ Aggiungi nuovo prodotto")
    with st.form("form_aggiunta"):
        codice_texture = st.text_input("Codice texture").strip().upper()
        nome_prodotto = st.text_input("Nome prodotto").strip()
        colori = st.text_input("Codici colore (separati da virgole)")
        naturalita = st.text_input("Naturalità (es: 98%)")
        mercati = st.text_input("Mercati (es: UE, USA, Cina)")
        segnalazioni = st.text_input("Segnalazioni (opzionale, separa con virgole)")
        clean_options = ["NO CLEAN", "CLEAN SEPHORA", "CLEAN CREDO", "CLEAN PHARMA COS"]
        clean = st.multiselect("Clean standard (puoi selezionarne più di uno)", clean_options)
        famiglia = st.selectbox("Famiglia", ["", "anidro", "emulsione", "polvere", "cotto", "ibrido"])
        spf = st.text_input("SPF (es: 30, lascia vuoto se non presente)")
        plumping = st.text_input("Plumping (lascia vuoto se non presente)")
        ph = st.text_input("pH (lascia vuoto se non presente)")
        talc_free = st.checkbox("Talc free")
        microplastic_free = st.checkbox("Microplastic free")
        paraben_free = st.checkbox("Paraben free")
        vegan = st.checkbox("Vegan")
        rspo = st.text_input("RSPO")
        campionabile = st.selectbox("Campionabile", ["", "campionabile", "non campionabile"])
        presente_in_sala = st.selectbox("Presente in sala campioni", ["", "sì", "no"])
        materiali_packaging = st.text_input("Materiali packaging")
        packaging = st.text_input("Packaging")
        test = st.text_input("Test effettuati (separati da virgole)")
        finish = st.selectbox("Finish", ["", "Matte", "Luminous", "Satin", "Velvet"])
        coprenza = st.selectbox("Coprenza", ["", "Leggera", "Media", "Alta"])
        note_mp = st.text_input("Note materie prime")
        costo = st.text_input("Costo al kg")
        submitted = st.form_submit_button("Salva prodotto")

        if submitted:
            nuovo_prodotto = {
                "codice_texture": codice_texture,
                "nome_prodotto": nome_prodotto,
                "colori": [c.strip().upper() for c in colori.split(",") if c.strip()],
                "naturalita": naturalita,
                "mercati": [m.strip() for m in mercati.split(",") if m.strip()],
                "segnalazioni": [s.strip() for s in segnalazioni.split(",") if s.strip()],
                "clean": clean,
                "famiglia": famiglia,
                "spf": spf,
                "plumping": plumping,
                "ph": ph,
                "talc_free": talc_free,
                "microplastic_free": microplastic_free,
                "paraben_free": paraben_free,
                "vegan": vegan,
                "rspo": rspo,
                "campionabile": campionabile,
                "presente_in_sala": presente_in_sala,
                "materiali_packaging": materiali_packaging.strip(),
                "packaging": packaging.strip(),
                "test": [t.strip() for t in test.split(",") if t.strip()],
                "finish": finish.strip(),
                "coprenza": coprenza.strip(),
                "note_materie_prime": note_mp.strip(),
                "costo_al_kg": costo.strip()
            }
            prodotti.append(nuovo_prodotto)
            save_data(prodotti)
            st.success("Prodotto aggiunto correttamente!")
