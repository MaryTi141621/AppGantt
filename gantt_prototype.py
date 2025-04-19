import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import os
from matplotlib.patches import Patch

class GanttPrototype:
    def __init__(self, excel_file=None):
        """
        Inizializza il prototipo di Gantt.
        
        Args:
            excel_file: Percorso del file Excel esistente (opzionale)
        """
        self.excel_file = excel_file
        
        # Crea un DataFrame vuoto per le attività se non viene fornito un file
        if excel_file and os.path.exists(excel_file):
            try:
                self.df = pd.read_excel(excel_file, sheet_name='Attività')
            except:
                self.initialize_dataframe()
        else:
            self.initialize_dataframe()
    
    def initialize_dataframe(self):
        """Inizializza un DataFrame vuoto con la struttura corretta"""
        self.df = pd.DataFrame(columns=[
            'ID', 'Nome_Attività', 'Data_Inizio', 'Data_Fine', 'Persona_Riferimento', 'Stato'
        ])
    
    def add_activity(self, nome, data_inizio, data_fine, persona, stato='In corso'):
        """
        Aggiunge una nuova attività al DataFrame.
        
        Args:
            nome: Nome dell'attività
            data_inizio: Data di inizio (formato stringa 'YYYY-MM-DD')
            data_fine: Data di fine (formato stringa 'YYYY-MM-DD')
            persona: Persona di riferimento
            stato: Stato dell'attività (default: 'In corso')
        """
        # Converti le date se sono stringhe
        if isinstance(data_inizio, str):
            data_inizio = pd.to_datetime(data_inizio)
        if isinstance(data_fine, str):
            data_fine = pd.to_datetime(data_fine)
        
        # Genera un nuovo ID
        if len(self.df) == 0:
            new_id = 1
        else:
            new_id = self.df['ID'].max() + 1
        
        # Aggiungi la nuova attività
        new_row = pd.DataFrame({
            'ID': [new_id],
            'Nome_Attività': [nome],
            'Data_Inizio': [data_inizio],
            'Data_Fine': [data_fine],
            'Persona_Riferimento': [persona],
            'Stato': [stato]
        })
        
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        return new_id
    
    def update_activity(self, id, **kwargs):
        """
        Aggiorna un'attività esistente.
        
        Args:
            id: ID dell'attività da aggiornare
            **kwargs: Coppie chiave-valore dei campi da aggiornare
        """
        if id not in self.df['ID'].values:
            print(f"Errore: Attività con ID {id} non trovata.")
            return False
        
        # Converti le date se sono stringhe
        if 'Data_Inizio' in kwargs and isinstance(kwargs['Data_Inizio'], str):
            kwargs['Data_Inizio'] = pd.to_datetime(kwargs['Data_Inizio'])
        if 'Data_Fine' in kwargs and isinstance(kwargs['Data_Fine'], str):
            kwargs['Data_Fine'] = pd.to_datetime(kwargs['Data_Fine'])
        
        # Aggiorna i campi
        for key, value in kwargs.items():
            if key in self.df.columns:
                self.df.loc[self.df['ID'] == id, key] = value
            else:
                print(f"Avviso: Campo '{key}' non presente nel DataFrame.")
        
        return True
    
    def delete_activity(self, id):
        """
        Elimina un'attività.
        
        Args:
            id: ID dell'attività da eliminare
        """
        if id not in self.df['ID'].values:
            print(f"Errore: Attività con ID {id} non trovata.")
            return False
        
        self.df = self.df[self.df['ID'] != id]
        return True
    
    def save_to_excel(self, file_path):
        """
        Salva il DataFrame in un file Excel.
        
        Args:
            file_path: Percorso del file Excel
        """
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            self.df.to_excel(writer, sheet_name='Attività', index=False)
            
            # Crea un foglio vuoto per il Gantt (sarà generato dinamicamente)
            pd.DataFrame().to_excel(writer, sheet_name='GANTT', index=False)
        
        print(f"File salvato: {file_path}")
        return file_path
    
    def generate_gantt(self, output_file, filter_person=None):
        """
        Genera un diagramma di Gantt basato sui dati delle attività.
        
        Args:
            output_file: Percorso dove salvare l'immagine del diagramma di Gantt
            filter_person: Filtra le attività per persona di riferimento (opzionale)
        """
        # Filtra il DataFrame se necessario
        if filter_person:
            df_filtered = self.df[self.df['Persona_Riferimento'] == filter_person].copy()
            title_suffix = f" - {filter_person}"
        else:
            df_filtered = self.df.copy()
            title_suffix = ""
        
        # Verifica che ci siano dati da visualizzare
        if len(df_filtered) == 0:
            print("Nessuna attività da visualizzare nel diagramma di Gantt.")
            return None
        
        # Ordina per data di inizio
        df_filtered = df_filtered.sort_values('Data_Inizio')
        
        # Crea la figura
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Formatta l'asse x per le date
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        plt.xticks(rotation=45)
        
        # Colori per gli stati
        colori_stati = {
            'Non iniziato': 'lightgrey',
            'In corso': 'lightblue',
            'Completato': 'lightgreen',
            'In ritardo': 'salmon',
            'In pausa': 'yellow'
        }
        
        # Aggiungi barre per ogni attività
        for i, task in df_filtered.iterrows():
            start_date = task['Data_Inizio']
            end_date = task['Data_Fine']
            
            # Calcola la durata in giorni
            duration = (end_date - start_date).days
            
            # Colore basato sullo stato
            color = colori_stati.get(task['Stato'], 'lightgrey')
            
            # Aggiungi la barra
            ax.barh(task['Nome_Attività'], duration, left=start_date, 
                    height=0.5, align='center', color=color, 
                    alpha=0.8, edgecolor='black')
            
            # Aggiungi il nome della persona di riferimento
            ax.text(end_date + timedelta(days=1), 
                   task['Nome_Attività'], 
                   task['Persona_Riferimento'], 
                   va='center')
        
        # Aggiungi titolo e etichette
        plt.title(f'Diagramma di Gantt{title_suffix}')
        plt.xlabel('Data')
        plt.ylabel('Attività')
        
        # Aggiungi una legenda per gli stati
        legend_elements = [Patch(facecolor=color, edgecolor='black', label=state)
                          for state, color in colori_stati.items()]
        ax.legend(handles=legend_elements, title='Stato', loc='upper right')
        
        # Imposta i limiti dell'asse x
        plt.xlim([
            df_filtered['Data_Inizio'].min() - timedelta(days=3),
            df_filtered['Data_Fine'].max() + timedelta(days=15)
        ])
        
        # Aggiungi griglia
        plt.grid(True, axis='x', alpha=0.3)
        
        # Salva il grafico
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        
        print(f'Diagramma di Gantt salvato in: {output_file}')
        return output_file
    
    def get_unique_persons(self):
        """Restituisce l'elenco delle persone di riferimento uniche"""
        return self.df['Persona_Riferimento'].unique().tolist()
    
    def get_activities_by_person(self, person):
        """Restituisce le attività filtrate per persona di riferimento"""
        return self.df[self.df['Persona_Riferimento'] == person]


# Esempio di utilizzo
if __name__ == '__main__':
    # Crea un'istanza del prototipo
    gantt = GanttPrototype()
    
    # Aggiungi alcune attività di esempio
    gantt.add_activity('Sviluppo frontend', '2024-05-01', '2024-05-15', 'Marco', 'In corso')
    gantt.add_activity('Sviluppo backend', '2024-05-10', '2024-05-30', 'Laura', 'Non iniziato')
    gantt.add_activity('Testing', '2024-05-25', '2024-06-05', 'Marco', 'Non iniziato')
    gantt.add_activity('Documentazione', '2024-06-01', '2024-06-10', 'Giulia', 'Non iniziato')
    gantt.add_activity('Deployment', '2024-06-10', '2024-06-15', 'Laura', 'Non iniziato')
    
    # Salva in Excel
    gantt.save_to_excel('gantt_prototype.xlsx')
    
    # Genera il diagramma di Gantt completo
    gantt.generate_gantt('gantt_completo.png')
    
    # Genera il diagramma di Gantt filtrato per persona
    gantt.generate_gantt('gantt_marco.png', filter_person='Marco')
