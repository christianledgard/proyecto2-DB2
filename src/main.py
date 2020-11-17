import nltk
from operator import itemgetter
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import json
import os

nltk.download('punkt')
nltk.download('stopwords')
stemmer = SnowballStemmer('spanish')


def pre_procesamiento(texto):
    """
    pre procesar text usando la librería nltk

    :param texto: archivo de texto a procesar
    """
    # Generar Tokens
    tokens = nltk.word_tokenize(texto)

    # StopList
    stop_list = stopwords.words("spanish")
    adicionales = ["«", "»", ".", ",", ";", "(", ")", ":", "@", "RT", "#", "|", "?", "!", "https", "$", "%", "&", "'", "''", "..", "..."]
    stop_list += adicionales

    # Remover de la lista los StopList Words
    tokens_clean = tokens.copy()
    for token in tokens:
        if token in stop_list:
            tokens_clean.remove(token)

    # Remplazar la palabra por su raíz (STEMMING)
    tokens_stremed = list()
    for token in tokens_clean:
        tokens_stremed.append(stemmer.stem(token))

    return tokens_stremed


def dic_palabras_con_terminos_mas_frecuentes(lista):
    """
    calcular document frequency

    :param lista: lista con terminos
    """
    frecuencia_palabras = dict()
    for lista_archivo in lista:
        for item in lista_archivo:
            if item in frecuencia_palabras:
                frecuencia_palabras[item][0] += 1
            else:
                frecuencia_palabras[item] = [1]

    return dict(sorted(frecuencia_palabras.items(), key=itemgetter(1), reverse=True))


def hallar_coincidencia_de_la_palabra_en_todos_los_tweets(palabra, id, index_list):
    if (len(index_list[palabra]) == 1): index_list[palabra].append([])
    encontrado = False
    for elemento_de_lista in index_list[palabra][1]:
        if elemento_de_lista[0] == id:
            elemento_de_lista[1] += 1
            encontrado = True
    if not encontrado:
        index_list[palabra][1].append([id,1])


def generar_index(grupos_de_palabras_con_id, index_list):
    for id in grupos_de_palabras_con_id:
        for palabra in grupos_de_palabras_con_id[id]:
            hallar_coincidencia_de_la_palabra_en_todos_los_tweets(palabra, id, index_list)
    return dict(sorted(index_list.items()))


def exportar_index(index, file_name):
    with open(file_name, 'w') as file:
        file.write(json.dumps(index))
    return True

def procesar_index(nombre_archivo):
    grupos_de_palabras_con_id = dict()
    grupos_de_palabras = list()
    with open(nombre_archivo) as arrayOfJsons:
        data = json.load(arrayOfJsons)
        for item in data:
            pre_procesado = pre_procesamiento(item["text"])
            grupos_de_palabras_con_id[item["id"]] = pre_procesado
            grupos_de_palabras.append(pre_procesado)
    return generar_index(grupos_de_palabras_con_id, dic_palabras_con_terminos_mas_frecuentes(grupos_de_palabras))


def bsb_index_construction(input_directory, output_directory):
    for block in os.listdir(input_directory):
        index = procesar_index(input_directory + "/" + block)
        exportar_index(index, output_directory + "/index-" + block)


def merge_blocks_helper(block1, block2):


def merge_blocks(directory):
    total_merge_blocks = len(os.listdir(directory)) // 2



# archivo = "clean/tweets_2018-08-07.json"
# index = procesar_index(archivo)
# exportar_index(index)
# print(index)

bsb_index_construction("clean", "index")

# hallar document frequency (# de documentos que contienen a t). trivial, tamaño de índice invertido sobre un término
# 