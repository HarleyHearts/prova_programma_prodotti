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
        risultati = [p for p in risultati if p.get("clean") == clean]
    if spf is not None:
        risultati = [p for p in risultati if bool(p.get("spf")) == spf]
    if microplastiche is not None:
        risultati = [p for p in risultati if p.get("microplastiche") == microplastiche]
    if talco is not None:
        risultati = [p for p in risultati if p.get("talco") == talco]
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

# ---- INTERFACCIA PRINCIPALE ----

st.sidebar.title("Navigazione")
pagina = st.sidebar.radio("Vai a:", ["Scheda prodotto", "Filtra prodotti", "Aggiungi prodotto"])

prodotti = load_data()

# ---- PAGINA 1: SCHEDA PRODOTTO ----
if pagina == "Scheda prodotto":
    st.title("📄 Scheda prodotto")
    codice_input = st.text_input("Inserisci codice texture o codice colore")
    prodotto = trova_prodotto(codice_input.strip().upper(), prodotti) if codice_input else None

    if prodotto:
        with st.form("modifica_prodotto"):
            st.subheader("Modifica prodotto")
            codice_texture = st.text_input("Codice texture", value=prodotto['codice_texture'])
            colori = st.text_input("Colori (separati da virgola)", value=", ".join(prodotto['colori']))
            naturalita = st.text_input("Naturalità", value=prodotto['naturalita'])
            mercati = st.text_input("Mercati (separati da virgola)", value=", ".join(prodotto['mercati']))
            segnalazioni = st.text_input("Segnalazioni", value=", ".join(prodotto['segnalazioni']))
            clean = st.checkbox("È clean?", value=prodotto['clean'])
            spf = st.text_input("SPF", value=prodotto.get('spf', ''))
            microplastiche = st.checkbox("Contiene microplastiche?", value=prodotto['microplastiche'])
            talco = st.checkbox("Contiene talco?", value=prodotto['talco'])
            packaging = st.text_input("Packaging", value=prodotto.get('packaging', ''))
            test = st.text_input("Test effettuati", value=", ".join(prodotto.get('test', [])))
            finish = st.selectbox("Finish", ["", "Matte", "Luminous", "Satin", "Velvet"], index=["", "Matte", "Luminous", "Satin", "Velvet"].index(prodotto.get('finish', '')))
            coprenza = st.selectbox("Coprenza", ["", "Leggera", "Media", "Alta"], index=["", "Leggera", "Media", "Alta"].index(prodotto.get('coprenza', '')))
            note_mp = st.text_input("Note materie prime", value=prodotto.get('note_materie_prime', ''))
            costo = st.text_input("Costo al kg", value=prodotto.get('costo_al_kg', ''))
            salva = st.form_submit_button("Salva modifiche")

            if salva:
                prodotto.update({
                    "codice_texture": codice_texture,
                    "colori": [c.strip().upper() for c in colori.split(",") if c.strip()],
                    "naturalita": naturalita,
                    "mercati": [m.strip() for m in mercati.split(",") if m.strip()],
                    "segnalazioni": [s.strip() for s in segnalazioni.split(",") if s.strip()],
                    "clean": clean,
                    "spf": spf,
                    "microplastiche": microplastiche,
                    "talco": talco,
                    "packaging": packaging.strip(),
                    "test": [t.strip() for t in test.split(",") if t.strip()],
                    "finish": finish.strip(),
                    "coprenza": coprenza.strip(),
                    "note_materie_prime": note_mp.strip(),
                    "costo_al_kg": costo.strip()
                })
                save_data(prodotti)
                st.success("Modifiche salvate correttamente!")

        st.download_button("📥 Esporta in Excel", data=esporta_excel([prodotto]), file_name="scheda_prodotto.xlsx")
        st.download_button("📄 Esporta in PDF", data=esporta_pdf(prodotto), file_name="scheda_prodotto.pdf")

# ---- PAGINA 2: FILTRA ----
elif pagina == "Filtra prodotti":
    st.title("🔎 Filtra prodotti")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filtro_clean = st.checkbox("Clean")
    with col2:
        filtro_spf = st.checkbox("SPF")
    with col3:
        filtro_micro = st.checkbox("Senza microplastiche")
    with col4:
        filtro_talco = st.checkbox("Senza talco")

    filtrati = filtra_prodotti(
        prodotti,
        clean=True if filtro_clean else None,
        spf=True if filtro_spf else None,
        microplastiche=False if filtro_micro else None,
        talco=False if filtro_talco else None
    )

    st.subheader(f"Risultati trovati: {len(filtrati)}")
    st.download_button("📥 Esporta risultati in Excel", data=esporta_excel(filtrati), file_name="prodotti_filtrati.xlsx")

    for prodotto in filtrati:
        with st.expander(prodotto['codice_texture']):
            st.text(f"Colori: {', '.join(prodotto['colori'])}")
            st.text(f"Naturalità: {prodotto['naturalita']}")
            st.text(f"Mercati: {', '.join(prodotto['mercati'])}")

# ---- PAGINA 3: AGGIUNGI ----
else:
    st.title("➕ Aggiungi nuovo prodotto")
    with st.form("form_aggiunta"):
        codice_texture = st.text_input("Codice texture").strip().upper()
        colori = st.text_input("Codici colore (separati da virgole)")
        naturalita = st.text_input("Naturalità (es: 98%)")
        mercati = st.text_input("Mercati (es: UE, USA, Cina)")
        segnalazioni = st.text_input("Segnalazioni (opzionale, separa con virgole)")
        clean = st.checkbox("È clean?")
        spf = st.text_input("SPF (es: 30, lascia vuoto se non presente)")
        microplastiche = st.checkbox("Contiene microplastiche?", value=False)
        talco = st.checkbox("Contiene talco?", value=False)
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
                "colori": [c.strip().upper() for c in colori.split(",") if c.strip()],
                "naturalita": naturalita,
                "mercati": [m.strip() for m in mercati.split(",") if m.strip()],
                "segnalazioni": [s.strip() for s in segnalazioni.split(",") if s.strip()],
                "clean": clean,
                "spf": spf,
                "microplastiche": microplastiche,
                "talco": talco,
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
