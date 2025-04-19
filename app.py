import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from gantt_prototype import GanttPrototype

# Configurazione della pagina
st.set_page_config(
    page_title="Prototipo Gantt",
    page_icon="📊",
    layout="wide"
)

# Titolo dell'applicazione
st.title("Prototipo Gantt con Filtro per Persona")

# Inizializzazione dello stato della sessione
if 'gantt' not in st.session_state:
    st.session_state.gantt = GanttPrototype()
    
if 'current_filter' not in st.session_state:
    st.session_state.current_filter = None

# Funzione per aggiornare il grafico Gantt
def update_gantt_chart():
    # Crea la directory per i grafici se non esiste
    os.makedirs('gantt_charts', exist_ok=True)
    
    # Genera il grafico Gantt
    if st.session_state.current_filter:
        chart_path = f"gantt_charts/gantt_{st.session_state.current_filter.replace(' ', '_')}.png"
        st.session_state.gantt.generate_gantt(chart_path, filter_person=st.session_state.current_filter)
    else:
        chart_path = "gantt_charts/gantt_completo.png"
        st.session_state.gantt.generate_gantt(chart_path)
    
    return chart_path

# Layout dell'applicazione con due colonne
col1, col2 = st.columns([1, 2])

# Colonna 1: Form per aggiungere/modificare attività
with col1:
    st.header("Gestione Attività")
    
    # Form per aggiungere una nuova attività
    with st.form("add_activity_form"):
        st.subheader("Aggiungi Nuova Attività")
        
        nome_attivita = st.text_input("Nome Attività")
        data_inizio = st.date_input("Data Inizio", value=datetime.now())
        data_fine = st.date_input("Data Fine", value=datetime.now() + timedelta(days=7))
        persona = st.text_input("Persona di Riferimento")
        
        stati = ['Non iniziato', 'In corso', 'Completato', 'In ritardo', 'In pausa']
        stato = st.selectbox("Stato", stati)
        
        submitted = st.form_submit_button("Aggiungi Attività")
        
        if submitted:
            if nome_attivita and persona:
                # Converti date in datetime
                data_inizio_dt = pd.to_datetime(data_inizio)
                data_fine_dt = pd.to_datetime(data_fine)
                
                # Verifica che la data di fine sia successiva alla data di inizio
                if data_fine_dt <= data_inizio_dt:
                    st.error("La data di fine deve essere successiva alla data di inizio.")
                else:
                    # Aggiungi l'attività
                    st.session_state.gantt.add_activity(nome_attivita, data_inizio_dt, data_fine_dt, persona, stato)
                    st.success(f"Attività '{nome_attivita}' aggiunta con successo!")
            else:
                st.error("Nome attività e persona di riferimento sono campi obbligatori.")
    
    # Visualizza la tabella delle attività
    st.subheader("Elenco Attività")
    
    if not st.session_state.gantt.df.empty:
        # Formatta le date per la visualizzazione
        df_display = st.session_state.gantt.df.copy()
        df_display['Data_Inizio'] = df_display['Data_Inizio'].dt.strftime('%d/%m/%Y')
        df_display['Data_Fine'] = df_display['Data_Fine'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(df_display)
        
        # Form per eliminare un'attività
        with st.form("delete_activity_form"):
            st.subheader("Elimina Attività")
            
            activity_ids = st.session_state.gantt.df['ID'].tolist()
            id_to_delete = st.selectbox("Seleziona ID Attività da Eliminare", activity_ids)
            
            delete_submitted = st.form_submit_button("Elimina Attività")
            
            if delete_submitted:
                if st.session_state.gantt.delete_activity(id_to_delete):
                    st.success(f"Attività con ID {id_to_delete} eliminata con successo!")
                else:
                    st.error(f"Impossibile eliminare l'attività con ID {id_to_delete}.")
    else:
        st.info("Nessuna attività presente. Aggiungi una nuova attività utilizzando il form sopra.")
    
    # Salva in Excel
    if not st.session_state.gantt.df.empty:
        if st.button("Salva in Excel"):
            file_path = st.session_state.gantt.save_to_excel("gantt_prototype.xlsx")
            st.success(f"Dati salvati in {file_path}")
            
            # Offri il download del file
            with open(file_path, "rb") as file:
                st.download_button(
                    label="Scarica file Excel",
                    data=file,
                    file_name="gantt_prototype.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Colonna 2: Visualizzazione del Gantt
with col2:
    st.header("Diagramma di Gantt")
    
    # Filtro per persona
    if not st.session_state.gantt.df.empty:
        persone = ['Tutte'] + st.session_state.gantt.get_unique_persons()
        selected_person = st.selectbox("Filtra per Persona", persone)
        
        if selected_person == 'Tutte':
            st.session_state.current_filter = None
        else:
            st.session_state.current_filter = selected_person
        
        # Genera e visualizza il grafico Gantt
        if len(st.session_state.gantt.df) > 0:
            chart_path = update_gantt_chart()
            st.image(chart_path)
        else:
            st.info("Aggiungi attività per visualizzare il diagramma di Gantt.")
    else:
        st.info("Nessuna attività presente. Aggiungi attività per visualizzare il diagramma di Gantt.")

# Istruzioni d'uso
with st.expander("Istruzioni d'uso"):
    st.markdown("""
    ### Come utilizzare questo prototipo:
    
    1. **Aggiungi attività** compilando il form nella colonna di sinistra
    2. **Visualizza il diagramma di Gantt** nella colonna di destra
    3. **Filtra per persona** utilizzando il menu a tendina sopra il diagramma
    4. **Elimina attività** utilizzando il form nella parte inferiore della colonna di sinistra
    5. **Salva in Excel** per esportare i dati
    
    Il diagramma di Gantt mostra le attività con colori diversi in base allo stato:
    - Grigio chiaro: Non iniziato
    - Blu chiaro: In corso
    - Verde chiaro: Completato
    - Rosso salmone: In ritardo
    - Giallo: In pausa
    """)
