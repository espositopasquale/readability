# app.py
# ─────────────────────────────────────────────────────────────────────────────
# Analisi leggibilità + vocabolario di base (VDB) fisso da "vdb.csv"
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import re
import unicodedata
from collections import Counter

st.set_page_config(page_title="Analisi VDB e leggibilità", layout="wide")

# ───────────────────────────── Utilità ─────────────────────────────

def strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")

def normalize_token(tok: str, ignore_accents: bool = True) -> str:
    tok = tok.replace("’", "'").replace("`", "'").strip("-' ")
    # Elisioni: l'acqua -> acqua ; nell', all', ecc.
    if "'" in tok:
        parts = [p for p in tok.split("'") if p]
        if parts:
            tok = parts[-1]
    tok = tok.replace("-", "")
    tok = tok.lower()
    if ignore_accents:
        tok = strip_accents(tok)
    return tok

def tokenize_it(text: str, ignore_accents: bool = True, drop_numeric: bool = True):
    raw_tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", text.replace("’", "'"))
    tokens = []
    for t in raw_tokens:
        nt = normalize_token(t, ignore_accents=ignore_accents)
        if not nt:
            continue
        if drop_numeric and any(ch.isdigit() for ch in nt):
            continue
        tokens.append(nt)
    return tokens

def split_sentences(text: str):
    parts = re.split(r"[.!?;:]+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]

def count_letters(text: str):
    return sum(1 for ch in text if ch.isalpha())

def gulpease(text: str, tokens: list[str], sentences: list[str]) -> float:
    L = count_letters(text)
    W = max(1, len(tokens))
    S = max(1, len(sentences))
    score = 89 + (300 * S - 10 * L) / W
    return max(0.0, min(100.0, score))

@st.cache_data
def load_vdb_df() -> pd.DataFrame:
    try:
        df = pd.read_csv("vdb.csv", sep=None, engine="python", dtype=str, keep_default_na=False)
    except Exception:
        df = pd.read_csv("vdb.csv", sep=r"\s+|[,;]", engine="python", dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    if not {"ita", "vdb_level"}.issubset(set(df.columns)):
        raise ValueError("Il file vdb.csv deve avere le colonne 'ita' e 'vdb_level'.")
    df["ita"] = df["ita"].astype(str).str.strip()
    df["vdb_level"] = df["vdb_level"].astype(str).str.strip()
    return df

@st.cache_data
def make_vocab_set(df: pd.DataFrame, include_levels, ignore_accents: bool = True):
    df_f = df[df["vdb_level"].isin({str(l) for l in include_levels})] if include_levels else df
    words = df_f["ita"].astype(str).tolist()
    norm = [normalize_token(w, ignore_accents=ignore_accents) for w in words if w]
    return set(w for w in norm if w)

def to_csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# ───────────────────────────── UI ─────────────────────────────

st.title("Analisi vocabolario di base e leggibilità")

with st.sidebar:
    st.header("Impostazioni")
    ignore_accents = st.checkbox("Ignora accenti", value=True)
    drop_numeric = st.checkbox("Escludi token con cifre", value=True)

    # Carica sempre vdb.csv
    try:
        vdb_df = load_vdb_df()
        lvls = sorted(vdb_df["vdb_level"].astype(str).unique().tolist(), key=lambda x: (len(x), x))
        default_lvls = [l for l in ["1", "2", "3"] if l in lvls] or lvls
        include_levels = st.multiselect("Livelli VDB da includere", lvls, default=default_lvls)
        vocab_set = make_vocab_set(vdb_df, include_levels, ignore_accents=ignore_accents)
        st.caption(f"Parole nel VDB attivo: {len(vocab_set)}")
    except FileNotFoundError:
        vocab_set = set()
        st.error("File 'vdb.csv' non trovato. Mettilo nella stessa cartella di app.py.")
    except Exception as e:
        vocab_set = set()
        st.error(f"Errore nel leggere 'vdb.csv': {e}")

st.subheader("Testo da analizzare")

# Usa session_state per pulizia elegante
# Gestione sicura dello stato del testo
if "text_input" not in st.session_state:
    st.session_state["text_input"] = ""

col_run, col_clear = st.columns([1, 1])

# Se si preme "Pulisci", azzera PRIMA di creare il text_area
if col_clear.button("Pulisci"):
    st.session_state["text_input"] = ""
    st.rerun()

text = st.text_area(
    "Incolla il testo qui sotto:",
    height=220,
    key="text_input",
    placeholder="Incolla il tuo testo…"
)

run = col_run.button("Analizza", type="primary")


# ───────────────────────────── Analisi ─────────────────────────────

if run:
    if not text.strip():
        st.warning("Inserisci prima un testo.")
    elif not vocab_set:
        st.warning("Vocabolario di base non disponibile. Controlla 'vdb.csv'.")
    else:
        tokens = tokenize_it(text, ignore_accents=ignore_accents, drop_numeric=drop_numeric)
        sentences = split_sentences(text)
        total_tokens = len(tokens)
        total_sentences = len(sentences)

        if total_tokens == 0:
            st.warning("Nessuna parola valida trovata con le impostazioni correnti.")
        else:
            # In/Out vocabolario
            in_flags = [t in vocab_set for t in tokens]
            in_count = sum(in_flags)
            out_count = total_tokens - in_count
            unique_tokens = set(tokens)
            unique_in = len([t for t in unique_tokens if t in vocab_set])
            unique_out = len(unique_tokens) - unique_in
            p_in = (in_count / total_tokens) * 100
            p_out = 100 - p_in

            # Indici di leggibilità
            g_score = gulpease(text, tokens, sentences)
            avg_sent_len = total_tokens / max(1, total_sentences)
            avg_word_len = sum(len(t) for t in tokens) / max(1, total_tokens)
            ttr = (len(unique_tokens) / total_tokens) * 100
            pct_long = (sum(1 for t in tokens if len(t) >= 7) / total_tokens) * 100

            # Pannelli principali
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Parole totali", f"{total_tokens}")
            c2.metric("Frasi", f"{total_sentences}")
            c3.metric("In VDB", f"{in_count}", f"{p_in:.1f}%")
            c4.metric("Fuori VDB", f"{out_count}", f"{p_out:.1f}%")
            c5.metric("Parole uniche (fuori/in)", f"{unique_out}/{unique_in}")

            st.subheader("Indici di leggibilità")
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Gulpease (0–100)", f"{g_score:.1f}")
            r2.metric("Parole/frase", f"{avg_sent_len:.2f}")
            r3.metric("Caratteri/parola", f"{avg_word_len:.2f}")
            r4.metric("TTR", f"{ttr:.1f}%")
            r5.metric("Parole lunghe (≥7)", f"{pct_long:.1f}%")

            # Elenco OOV
            oov_tokens = [t for t in tokens if t not in vocab_set]
            if oov_tokens:
                freq = Counter(oov_tokens)
                st.subheader("Parole fuori vocabolario (per frequenza)")
                top_n = st.slider("Quante righe mostrare", 5, 200, 30, step=5)
                df_oov = pd.DataFrame(
                    [{"parola": w, "frequenza": c} for w, c in freq.most_common(top_n)]
                )
                st.dataframe(df_oov, use_container_width=True)

                # download completo
                df_all = pd.DataFrame([{"parola": w, "frequenza": c} for w, c in freq.most_common()])
                st.download_button(
                    label="Scarica elenco completo (CSV)",
                    data=to_csv_download(df_all),
                    file_name="parole_fuori_vocabolario.csv",
                    mime="text/csv"
                )
            else:
                st.info("Tutte le parole del testo risultano nel vocabolario di base selezionato.")

        with st.expander("Dettagli e note"):
            st.markdown(
                """
**Gulpease**: indice (0–100) pensato per l’italiano; valori più alti = testo più semplice.  
Calcolato come: 89 + (300×frasi − 10×lettere) / parole.

**TTR**: rapporto tra tipi lessicali distinti e token totali (%), indicatore di varietà lessicale.

Le opzioni *Ignora accenti* e *Escludi token con cifre* si applicano al testo e al VDB.
                """
            )

st.caption("© 2025 — Analisi VDB e leggibilità")
