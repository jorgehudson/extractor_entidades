import openai
from trafilatura import extract, downloads, fetch_url
from ecommercetools import seo
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity 
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd

language_stopwords = stopwords.words('spanish')
non_words = list(punctuation)

# Funciones
def remove_stop_words(dirty_text):
    cleaned_text = ''
    for word in dirty_text.split():
        if word in language_stopwords or word in non_words:
            continue
        else:
            cleaned_text += word + ' '
    return cleaned_text


# API OpenAI KEY
openai.api_key = "AQUÍ TU CLAVE API"

keyword = input("Introduce keyword para comparar textos y extraer entidades de SERP: ")

urls = seo.get_serps(keyword)

# Arrays de datos
urlcontenidos = []
contenidos = []
entidades = []
tokens_gastados = []
dinero_gastado = []

orden = """"
Texto: <<Información>>
Extrae las entidades del texto anterior y muéstralas en un listado junto con el tipo de entidad correspondiente y sin repeticiones.
"""
for url in urls['link']:
    try:
        downloaded = fetch_url(url)
        downloaded is None
        resultweb = extract(downloaded, include_tables=None)
        texto_limpio = remove_stop_words(resultweb)
        
        if texto_limpio:           
            premisa = orden.replace('<<Información>>', resultweb)
            response = openai.Completion.create(
                engine = "text-davinci-003",
                prompt = premisa,
                temperature = 0.3,
                max_tokens=3000,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1
            )
            
        outlinep1 = response['choices'][0]['text']
        total_tokens = response['usage']['total_tokens']
        PRECIO = total_tokens/1000 * 0.02

        if outlinep1:
            urlcontenidos.append(url)
            contenidos.append(resultweb)
            entidades.append(outlinep1)
            tokens_gastados.append(str(total_tokens))
            dinero_gastado.append(str(PRECIO)+" €")
                      
    except:
        print("ERROR EN LA WEB: "+ url)

csv = pd.DataFrame(list(zip(urlcontenidos, contenidos, entidades, dinero_gastado, tokens_gastados)),columns=["URL", "Contenido", "Entidades", "Dinero gastado", "Tokens Gastados"]).to_csv(f"entidades_{keyword}.csv", index=False)