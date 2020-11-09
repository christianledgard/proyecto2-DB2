import nltk
from operator import itemgetter
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import json

nltk.download('punkt')
nltk.download('stopwords')
stemmer = SnowballStemmer('spanish')


def preProcesamiento(texto):
    # Generar Tokens
    tokens = nltk.word_tokenize(texto)

    # StopList
    stopList = stopwords.words("spanish")
    adicionales = ["«", "»", ".", ",", ";", "(", ")", ":", "@", "RT", "#", "|", "?", "!"]
    stopList += adicionales

    # Remover de la lista los StopList Words
    tokensClean = tokens.copy()
    for token in tokens:
        if token in stopList:
            tokensClean.remove(token)

    # Remplazar la palabra por su raíz (STEMMING)
    tokensStremed = list()
    for token in tokensClean:
        tokensStremed.append(stemmer.stem(token))

    return tokensStremed


def dicPalabrasConTerminosMasFrecuentes(lista):
    frecuenciaPalabras = {}
    for listaArchivo in lista:
        for item in listaArchivo:
            if (item in frecuenciaPalabras):
                frecuenciaPalabras[item][0] += 1
            else:
                frecuenciaPalabras[item] = [1]

    return dict(sorted(frecuenciaPalabras.items(), key=itemgetter(1), reverse=True))


def generarIndex(gruposDePalabrasConID, diccionarioConFrecuencias):
    indexList = diccionarioConFrecuencias

    for id in gruposDePalabrasConID:
        for palabra in gruposDePalabrasConID[id]:

            if (len(indexList[palabra]) == 1): indexList[palabra].append([])

            encontrado = False
            for elementoDeLista in indexList[palabra][1]:
                if elementoDeLista[0] == id:
                    elementoDeLista[1] += 1
                    encontrado = True
            if not encontrado:
                indexList[palabra][1].append([id,1])


    return dict(sorted(indexList.items(), key=itemgetter(1), reverse=True))

def exportarIndex(index):
    with open('index.json', 'w') as file:
        file.write(json.dumps(index))
    return True


listaDeArchivos = ["clean/tweets_2018-08-07.json"]


gruposDePalabrasConID = dict()
gruposDePalabras = list()
for archivo in listaDeArchivos:
    with open(archivo) as arrayOfJsons:
        data = json.load(arrayOfJsons)
        for item in data:
            preProcesado = preProcesamiento(item["text"])
            gruposDePalabrasConID[item["id"]] = preProcesado
            gruposDePalabras.append(preProcesado)



index = generarIndex(gruposDePalabrasConID, dicPalabrasConTerminosMasFrecuentes(gruposDePalabras))
exportarIndex(index)
print(index)