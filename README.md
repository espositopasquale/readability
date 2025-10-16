# 🧠 Analisi del Vocabolario di Base e della Leggibilità (Streamlit)

Un’applicazione web sviluppata in **Python** con **Streamlit** per analizzare testi in lingua italiana, misurandone la **leggibilità** e la **copertura lessicale** rispetto al *Vocabolario di Base della lingua italiana* (VDB) di **Tullio De Mauro (1999, 2016a, 2019)**.  
Il progetto nasce come strumento per **docenti, linguisti, redattori e studenti**, utile per valutare la semplicità, la chiarezza e l’accessibilità linguistica dei testi.

---

## 🚀 Funzionalità principali

- 🔍 **Analisi automatica del testo**: segmentazione in frasi e token, conteggio di parole e caratteri.  
- 🧩 **Vocabolario di Base (VDB)**: confronto tra il testo e il lessico di riferimento di De Mauro, suddiviso in livelli.  
- 📈 **Indice di leggibilità Gulpease** – sviluppato per la lingua italiana (Lucisano & Piemontese, 1988; v. Dell’Orletta et al., 2011).  
- 📊 **Indicatori linguistici complementari**:
  - Lunghezza media delle frasi e delle parole
  - Varietà lessicale (**TTR** – Type Token Ratio)
  - Percentuale di parole lunghe (≥7 caratteri)
- 📂 **Esportazione CSV** delle parole fuori vocabolario (OOV).  
- ⚙️ **Impostazioni personalizzabili**:
  - Ignora accenti
  - Escludi token numerici
  - Selezione livelli del VDB (1, 2, 3…)

---

## 🗂️ Struttura del progetto

