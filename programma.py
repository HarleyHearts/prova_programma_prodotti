
import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from fpdf import FPDF

data_file = "prodotti.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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

if pagina == "Scheda prodotto":
    st.title("📄 Scheda prodotto")
    ricerca = st.text_input("Cerca per codice texture o colore (anche parziale)").strip().upper()
    if ricerca:
        risultati = [p for p in prodotti if ricerca in p["codice_texture"] or any(ricerca in c for c in p["colori"])]
        if risultati:
            opzioni = [f"{p['codice_texture']} – {p.get('nome_prodotto', '')}" for p in risultati]
            scelta = st.selectbox("Seleziona un prodotto", opzioni)
            prodotto = risultati[opzioni.index(scelta)]
            for key, value in prodotto.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                st.write(f"**{key.replace('_', ' ').capitalize()}:** {value}")
            if st.button("Esporta scheda in PDF"):
                pdf_bytes = esporta_pdf(prodotto)
                st.download_button(label="Download PDF", data=pdf_bytes, file_name=f"{prodotto['codice_texture']}_scheda.pdf")
        else:
            st.warning("Nessun prodotto trovato.")

elif pagina == "Filtra prodotti":
    st.title("🔍 Filtra prodotti")
    with st.form("filtro_form"):
        filtro_clean = st.multiselect("Filtra per clean", ["NO CLEAN", "CLEAN SEPHORA", "CLEAN CREDO", "CLEAN PHARMA COS"])
        filtro_famiglia = st.selectbox("Famiglia", ["", "anidro", "emulsione", "polvere", "cotto", "ibrido"])
        filtro_microplastic = st.checkbox("Solo microplastic free")
        filtro_talc = st.checkbox("Solo talc free")
        filtro_paraben = st.checkbox("Solo paraben free")
        filtro_vegan = st.checkbox("Solo vegan")
        filtro_campionabile = st.selectbox("Campionabile", ["", "campionabile", "non campionabile"])
        filtro_sala = st.selectbox("Presente in sala campioni", ["", "sì", "no"])
        filtro_mercati = st.multiselect("Mercati target", ["UE", "USA", "Cina", "Australia", "UK", "Giappone", "Canada"])
        naturalita_min = st.number_input("Naturalità minima (%)", min_value=0, max_value=100, step=1, value=0)
        submit_filtro = st.form_submit_button("Applica filtro")

    if submit_filtro:
        risultati = prodotti
        if filtro_clean:
            risultati = [p for p in risultati if any(c in p.get("clean", []) for c in filtro_clean)]
        if filtro_famiglia:
            risultati = [p for p in risultati if p.get("famiglia") == filtro_famiglia]
        if filtro_microplastic:
            risultati = [p for p in risultati if p.get("microplastic_free") == True]
        if filtro_talc:
            risultati = [p for p in risultati if p.get("talc_free") == True]
        if filtro_paraben:
            risultati = [p for p in risultati if p.get("paraben_free") == True]
        if filtro_vegan:
            risultati = [p for p in risultati if p.get("vegan") == True]
        if filtro_campionabile:
            risultati = [p for p in risultati if p.get("campionabile") == filtro_campionabile]
        if filtro_sala:
            risultati = [p for p in risultati if p.get("presente_in_sala") == filtro_sala]
        if filtro_mercati:
            risultati = [p for p in risultati if any(m in p.get("mercati", []) for m in filtro_mercati)]
        if naturalita_min:
            risultati = [p for p in risultati if int(p.get("naturalita", "0").replace("%", "")) >= naturalita_min]

        st.write(f"Trovati {len(risultati)} prodotti")
        for p in risultati:
            st.markdown(f"**{p['codice_texture']} – {p.get('nome_prodotto', '')}**")
            st.markdown(", ".join(p.get("colori", [])))
            st.markdown(f"Famiglia: {p.get('famiglia', '')} | Clean: {', '.join(p.get('clean', []))}")
            st.markdown("---")
        if risultati:
            if st.button("Esporta risultati in Excel"):
                excel_bytes = esporta_excel(risultati)
                st.download_button(label="Download Excel", data=excel_bytes, file_name="prodotti_filtrati.xlsx")

elif pagina == "Aggiungi prodotto":
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
