import spacy

# 1. Estratto testuale del De Bello Gallico (Libro I, incipit)
text = """
Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae,
aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.
Hi omnes lingua, institutis, legibus inter se differunt.
Gallos ab Aquitanis Garumna flumen, a Belgis Matrona et Sequana dividit.
Horum omnium fortissimi sunt Belgae, propterea quod a cultu atque humanitate
provinciae longissime absunt, minimeque ad eos mercatores saepe commeant
atque ea quae ad effeminandos animos pertinent important, proximique sunt
Germanis, qui trans Rhenum incolunt, quibuscum continenter bellum gerunt.
"""

# 2. Caricare il modello di spaCy per il latino
# (installalo prima con: python -m spacy download la_core_news_sm)
nlp = spacy.load("la_core_news_sm")

# 3. Analizzare il testo
doc = nlp(text)

# 4. Stampare entità riconosciute
print("=== Named Entities trovate da spaCy ===")
for ent in doc.ents:
    print(f"{ent.text}  -->  {ent.label_}")

# 5. Visualizzare le frasi con le entità trovate
print("\n=== Frasi annotate ===")
for sent in doc.sents:
    ents = [f"{ent.text} ({ent.label_})" for ent in sent.ents]
    print(f"- {sent.text.strip()}")
    if ents:
        print("   ↳ Entità:", ", ".join(ents))
