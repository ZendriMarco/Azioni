import streamlit as st
from datetime import datetime

# Import condizionale delle funzioni personalizzate
try:
    from azioni_functions import (
        carica_dati, 
        aggiungi_record_streamlit,
        calcola_valore_totale,
        calcola_statistiche_portafoglio,
        valida_input,
        formatta_record_per_display,
        elimina_record,
        ottieni_quotazione_azione,
        esporta_dati_csv
    )
    FUNCTIONS_LOADED = True
except ImportError as e:
    st.error(f"⚠️ Errore nell'importazione del modulo azioni_functions: {e}")
    st.info("Assicurati che il file 'azioni_functions.py' sia nella stessa directory")
    FUNCTIONS_LOADED = False

# Configurazione pagina
st.set_page_config(
    page_title="📈 Archivio Azioni",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not FUNCTIONS_LOADED:
    st.stop()

# FUNZIONI AUSILIARIE PER GESTIRE ERRORI
@st.cache_data
def safe_load_data():
    """Carica i dati in modo sicuro"""
    try:
        return carica_dati()
    except Exception as e:
        st.error(f"Errore nel caricamento dati: {e}")
        return []

# INIZIALIZZAZIONE SESSION STATE
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = {}

if 'dati' not in st.session_state:
    st.session_state.dati = safe_load_data()

if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False

# SIDEBAR
with st.sidebar:
    st.header("🛠️ Strumenti")

    # Statistiche rapide
    try:
        stats = calcola_statistiche_portafoglio(st.session_state.dati)
        st.metric("💰 Valore Totale Investito", f"€{stats['totale_valore']:,.2f}")
        st.metric("📈 Posizioni", stats['numero_posizioni'])
        st.metric("🎯 Tickers Unici", stats['tickers_unici'])
    except Exception as e:
        st.error(f"Errore nel calcolo statistiche: {e}")

    st.markdown("---")

    # Export dati
    if st.session_state.dati:
        try:
            csv_data = esporta_dati_csv(st.session_state.dati)
            st.download_button(
                label="📥 Esporta CSV",
                data=csv_data,
                file_name=f"portafoglio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Errore nell'export CSV: {e}")

    # Ricerca quotazioni
    st.markdown("---")
    st.subheader("🔍 Quotazioni")
    ticker_ricerca = st.text_input("Ticker da ricercare:", key="ticker_search")
    if st.button("Cerca Quotazione", key="search_quote"):
        if ticker_ricerca:
            with st.spinner("Ricerca in corso..."):
                try:
                    quotazione = ottieni_quotazione_azione(ticker_ricerca)
                    st.session_state.quotazione_result = quotazione
                except Exception as e:
                    st.error(f"Errore nella ricerca quotazione: {e}")

# TITOLO PRINCIPALE
st.title("📈 Archivio Azioni")
st.markdown("**Gestione del tuo portafoglio di investimenti**")
st.markdown("---")

# TAB NAVIGATION
tab1, tab2, tab3 = st.tabs(["📝 Inserimento", "📊 Portafoglio", "🔧 Utilità"])

# TAB 1: INSERIMENTO
with tab1:
    st.header("📝 Inserimento Nuova Azione")
    
    with st.form(key=f"form_azioni_{st.session_state.form_key}"):
        col1, col2 = st.columns(2)

        with col1:
            text_azione = st.text_input("🏢 Nome Azione", help="Es: Apple, Microsoft, Tesla")
            text_prezzo = st.text_input("💰 Prezzo (€)", help="Prezzo di acquisto per azione")

        with col2:
            text_ticker = st.text_input("🎯 Ticker", help="Es: AAPL, MSFT, TSLA")
            text_quantita = st.text_input("📊 Quantità", help="Numero di azioni acquistate")

        # Anteprima calcolo
        if text_prezzo and text_quantita:
            try:
                valore_anteprima = float(text_prezzo) * float(text_quantita)
                st.info(f"💡 **Valore totale:** €{valore_anteprima:,.2f}")
            except ValueError:
                st.warning("⚠️ Inserisci valori numerici validi per prezzo e quantità")

        submitted = st.form_submit_button("➕ Aggiungi Azione", type="primary")

        if submitted:
            try:
                # Validazione input
                errori = valida_input(text_azione, text_ticker, text_prezzo, text_quantita)

                if errori:
                    for errore in errori:
                        st.error(f"❌ {errore}")
                else:
                    # Salvataggio dati processati
                    st.session_state.processed_data = {
                        'azione': text_azione.upper(),
                        'ticker': text_ticker.upper() if text_ticker else "",
                        'prezzo': text_prezzo if text_prezzo else "",
                        'quantita': text_quantita if text_quantita else ""
                    }

                    # Aggiunta record
                    record = aggiungi_record_streamlit(text_azione, text_ticker, text_prezzo, text_quantita, st.session_state)

                    if record:
                        st.success(f"✅ **Record aggiunto con successo!**")
                        st.success(f"📋 {text_azione} ({text_ticker}) - €{text_prezzo} x {text_quantita}")
                        st.session_state.form_key += 1
                        st.rerun()
                    else:
                        st.error("❌ **Errore nell'inserimento dei dati**")
            except Exception as e:
                st.error(f"❌ **Errore imprevisto:** {e}")

    # Mostra ultimo record aggiunto
    if st.session_state.processed_data:
        st.markdown("---")
        st.subheader("✅ Ultimo Record Aggiunto")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**🏢 Azione:** {st.session_state.processed_data.get('azione', '')}")
            st.write(f"**💰 Prezzo:** €{st.session_state.processed_data.get('prezzo', '0')}")
        with col2:
            st.write(f"**🎯 Ticker:** {st.session_state.processed_data.get('ticker', '')}")
            st.write(f"**📊 Quantità:** {st.session_state.processed_data.get('quantita', '0')}")

# TAB 2: PORTAFOGLIO
with tab2:
    if st.session_state.dati:
        st.header("📊 Il Tuo Portafoglio")

        try:
            # Statistiche
            stats = calcola_statistiche_portafoglio(st.session_state.dati)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Valore Totale Investito", f"€{stats['totale_valore']:,.2f}")
            with col2:
                st.metric("📈 N° Posizioni", stats['numero_posizioni'])
            with col3:
                st.metric("📊 Valore Medio", f"€{stats['valore_medio']:,.2f}")
            with col4:
                st.metric("🎯 Tickers Unici", stats['tickers_unici'])

            st.markdown("### 📋 Dettaglio Posizioni")

            # Visualizzazione posizioni
            for i, record in enumerate(st.session_state.dati):
                try:
                    record_formattato = formatta_record_per_display(record, i+1, stats['totale_valore'])

                    if record_formattato:
                        with st.expander(
                            f"📊 **Posizione {record_formattato['indice']}:** {record_formattato['azione']} ({record_formattato['ticker']}) - €{record_formattato['valore_posizione']:,.2f} ({record_formattato['percentuale']:.1f}%)",
                            expanded=False
                        ):
                            col1, col2, col3 = st.columns([2, 2, 1])

                            with col1:
                                st.write(f"**🏢 Azienda:** {record_formattato['azione']}")
                                st.write(f"**🎯 Ticker:** {record_formattato['ticker']}")
                                st.write(f"**💰 Prezzo unitario:** €{record_formattato['prezzo']:.2f}")

                            with col2:
                                st.write(f"**📊 Quantità:** {record_formattato['quantita']:,}")
                                st.write(f"**💎 Valore totale:** €{record_formattato['valore_posizione']:,.2f}")
                                st.write(f"**📅 Data:** {record_formattato['data_inserimento']}")

                            with col3:
                                if st.button(f"🗑️ Elimina", key=f"delete_{i}"):
                                    try:
                                        eliminated = elimina_record(st.session_state.dati, i)
                                        if eliminated:
                                            st.success("Record eliminato!")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Errore nell'eliminazione: {e}")

                            if record_formattato['percentuale'] > 0:
                                st.progress(min(record_formattato['percentuale'] / 100, 1.0))
                                st.caption(f"Peso nel portafoglio: {record_formattato['percentuale']:.1f}%")
                    else:
                        st.error(f"❌ Errore nella visualizzazione della posizione {i+1}")
                except Exception as e:
                    st.error(f"❌ Errore nel processamento record {i+1}: {e}")
        except Exception as e:
            st.error(f"❌ Errore nella visualizzazione portafoglio: {e}")
    else:
        st.info("📝 Nessuna posizione inserita ancora. Vai alla sezione 'Inserimento' per aggiungere le tue prime azioni!")

# TAB 3: UTILITÀ
with tab3:
    st.header("🔧 Utilità")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧹 Gestione Form")
        if st.button("🧹 Pulisci Form", help="Svuota tutti i campi del form"):
            st.session_state.form_key += 1
            st.session_state.processed_data = {}
            st.success("Form pulito!")
            st.rerun()

    with col2:
        st.subheader("🔍 Debug")
        if st.button("🔍 Toggle Debug", help="Mostra/nascondi dati di debug"):
            st.session_state.show_debug = not st.session_state.show_debug

    # Debug section
    if st.session_state.show_debug:
        st.markdown("---")
        st.subheader("🔍 Debug - Struttura Dati")
        try:
            st.json(st.session_state.dati)
        except Exception as e:
            st.error(f"Errore nella visualizzazione debug: {e}")

    # Test connessioni
    st.markdown("---")
    st.subheader("🔗 Test Connessioni")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Salvataggio JSON"):
            try:
                from azioni_functions import salva_dati
                result = salva_dati(st.session_state.dati)
                if result:
                    st.success("✅ Salvataggio JSON funzionante")
                else:
                    st.error("❌ Errore nel salvataggio JSON")
            except Exception as e:
                st.error(f"❌ Errore test salvataggio: {e}")

    with col2:
        if st.button("Test API Perplexity"):
            try:
                test_response = ottieni_quotazione_azione("AAPL")
                if "Errore" not in test_response:
                    st.success("✅ API Perplexity funzionante")
                    st.info("Risposta ricevuta (primi 100 caratteri):")
                    st.text(test_response[:100] + "...")
                else:
                    st.warning(f"⚠️ {test_response}")
            except Exception as e:
                st.error(f"❌ Errore test API: {e}") 

    # Risultato ricerca quotazioni
    if hasattr(st.session_state, 'quotazione_result'):
        st.markdown("---")
        st.subheader("💹 Risultato Ricerca Quotazione")
        st.write(st.session_state.quotazione_result)

# FOOTER
st.markdown("---")
st.caption("💾 I dati vengono salvati automaticamente nel file 'azioni.json'")
if st.session_state.dati:
    st.caption(f"📊 Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Info sulla versione
with st.expander("ℹ️ Info Versione"):
    st.write("**Versione:** 2.0 - Gestione errori migliorata")
    st.write("**Data:** Settembre 2025")
    st.write("**Caratteristiche:** Modularità, gestione errori robusta, test connessioni")
