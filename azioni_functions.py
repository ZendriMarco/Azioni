import json
from datetime import datetime

# Nome del file JSON per salvare i dati
NOME_FILE = "azioni.json"

def carica_dati():
    try:
        with open(NOME_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def salva_dati(dati):
    try:
        with open(NOME_FILE, 'w', encoding='utf-8') as file:
            json.dump(dati, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Errore nel salvataggio: {e}")
        return False

def aggiungi_record_puro(dati, azione, ticker, prezzo, quantita):
    try:
        prezzo_float = float(prezzo) if prezzo else 0.0
        quantita_float = float(quantita) if quantita else 0

        record = {
            "azione": azione,
            "ticker": ticker,
            "prezzo": prezzo_float,
            "quantita": quantita_float,
            "valore_totale": prezzo_float * quantita_float,
            "timestamp": datetime.now().isoformat(),
            "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        dati.append(record)
        salva_dati(dati)
        return record
    except ValueError:
        return None
    except Exception as e:
        return None

def aggiungi_record_streamlit(azione, ticker, prezzo, quantita, session_state):
    try:
        prezzo_float = float(prezzo) if prezzo else 0.0
        quantita_float = float(quantita) if quantita else 0

        record = {
            "azione": azione,
            "ticker": ticker,
            "prezzo": prezzo_float,
            "quantita": quantita_float,
            "valore_totale": prezzo_float * quantita_float,
            "timestamp": datetime.now().isoformat(),
            "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        session_state.dati.append(record)
        salva_dati(session_state.dati)
        return record
    except ValueError:
        return None
    except Exception as e:
        return None

def calcola_valore_totale(record):
    try:
        # Se il campo valore_totale esiste, usalo
        if 'valore_totale' in record and record['valore_totale'] is not None:
            return float(record['valore_totale'])
        # Altrimenti calcolalo dai campi prezzo e quantita
        prezzo = float(record.get('prezzo', 0))
        quantita = float(record.get('quantita', 0))
        return prezzo * quantita
    except (ValueError, TypeError):
        return 0.0

def response(query, model="sonar"):
    try:
        # Import condizionale per evitare errori se la libreria non è installata
        from dotenv import load_dotenv
        load_dotenv()

        # Prova ad importare Perplexity
        try:
            from perplexity import Perplexity
            client = Perplexity()
            completion = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": query
                }]
            )
            return completion.choices[0].message.content
        except ImportError:
            return f"Libreria Perplexity non installata."
        except Exception as e:
            return f"Errore API Perplexity: {e}"
    except Exception as e:
        return f"Errore generale: {e}"
def calcola_statistiche_portafoglio(dati):
    if not dati:
        return {
            'totale_valore': 0.0,
            'numero_posizioni': 0,
            'valore_medio': 0.0,
            'tickers_unici': 0
        }

    totale_valore = sum(calcola_valore_totale(record) for record in dati)
    numero_posizioni = len(dati)
    tickers_unici = len(set(record.get('ticker', '') for record in dati if record.get('ticker')))
    valore_medio = totale_valore / numero_posizioni if numero_posizioni > 0 else 0

    return {
        'totale_valore': totale_valore,
        'numero_posizioni': numero_posizioni,
        'valore_medio': valore_medio,
        'tickers_unici': tickers_unici
    }

def valida_input(azione, ticker, prezzo, quantita):
    """Valida gli input per l'inserimento di un record"""
    errori = []

    if not azione or not azione.strip():
        errori.append("Il nome dell'azione è obbligatorio")

    if prezzo:
        try:
            float(prezzo)
        except ValueError:
            errori.append("Il prezzo deve essere un numero decimale valido")

    if quantita:
        try:
            float(quantita)
        except ValueError:
            errori.append("La quantità deve essere un numero valido")

    return errori

def formatta_record_per_display(record, indice, totale_valore):
    try:
        valore_posizione = calcola_valore_totale(record)
        percentuale = (valore_posizione / totale_valore * 100) if totale_valore > 0 else 0

        return {
            'indice': indice,
            'azione': record.get('azione', 'Azione sconosciuta'),
            'ticker': record.get('ticker', 'N/A'),
            'prezzo': float(record.get('prezzo', 0)),
            'quantita': float(record.get('quantita', 0)),
            'valore_posizione': valore_posizione,
            'percentuale': percentuale,
            'data_inserimento': record.get('data_inserimento', record.get('timestamp', 'N/A'))
        }
    except Exception as e:
        return None

def elimina_record(dati, indice):
    try:
        if 0 <= indice < len(dati):
            record_eliminato = dati.pop(indice)
            salva_dati(dati)
            return record_eliminato
        return None
    except Exception as e:
        return None

def cerca_azioni_per_ticker(dati, ticker):
    if not ticker:
        return []

    ticker_upper = ticker.upper()
    return [record for record in dati if record.get('ticker', '').upper() == ticker_upper]

def ottieni_quotazione_azione(ticker):
    if not ticker:
        return "Ticker non specificato"

    query = f"Trovami la quotazione attuale di {ticker} e il prezzo delle azioni"
    return response(query)

def esporta_dati_csv(dati):
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Intestazioni
    writer.writerow(['Azione', 'Ticker', 'Prezzo', 'Quantità', 'Valore Totale', 'Data Inserimento'])

    # Dati
    for record in dati:
        writer.writerow([
            record.get('azione', ''),
            record.get('ticker', ''),
            record.get('prezzo', 0),
            record.get('quantita', 0),
            calcola_valore_totale(record),
            record.get('data_inserimento', record.get('timestamp', ''))
        ])

    return output.getvalue()
