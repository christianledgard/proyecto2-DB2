import nltk
from operator import itemgetter
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import json
import os

nltk.download('punkt')
nltk.download('stopwords')
stemmer = SnowballStemmer('spanish')

class Index:
    total_documents = 0

    def pre_procesamiento(self, texto):
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


    def dic_palabras_con_terminos_mas_frecuentes(self, lista):
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


    def hallar_coincidencia_de_la_palabra_en_todos_los_tweets(self, palabra, id, index_list):
        if (len(index_list[palabra]) == 1): index_list[palabra].append([])
        encontrado = False
        for elemento_de_lista in index_list[palabra][1]:
            if elemento_de_lista[0] == id:
                elemento_de_lista[1] += 1
                encontrado = True
        if not encontrado:
            index_list[palabra][1].append([id,1])


    def generar_index(self, grupos_de_palabras_con_id, index_list):
        for id in grupos_de_palabras_con_id:
            for palabra in grupos_de_palabras_con_id[id]:
                self.hallar_coincidencia_de_la_palabra_en_todos_los_tweets(palabra, id, index_list)
        return dict(sorted(index_list.items()))


    def exportar_index(self, index, file_name):
        with open(file_name, 'w') as file:
            file.write(json.dumps(index))
        return True

    def procesar_index(self, nombre_archivo):
        grupos_de_palabras_con_id = dict()
        grupos_de_palabras = list()
        with open(nombre_archivo) as arrayOfJsons:
            data = json.load(arrayOfJsons)
            self.total_documents += len(data)
            for item in data:
                pre_procesado = self.pre_procesamiento(item["text"])
                grupos_de_palabras_con_id[item["id"]] = pre_procesado
                grupos_de_palabras.append(pre_procesado)
        return self.generar_index(grupos_de_palabras_con_id, self.dic_palabras_con_terminos_mas_frecuentes(grupos_de_palabras))


    def bsb_index_construction(self, input_directory, output_directory):
        for block in os.listdir(input_directory):
            index = self.procesar_index(input_directory + "/" + block)
            self.exportar_index(index, output_directory + "/index-" + block)
            break


    def merge_blocks_helper(self, block1, block2):
        pass # comment explaining why this function is empty



    def merge_blocks(self, directory):
        
        pass #total_merge_blocks = len(os.listdir(directory)) // 2

    def get_file_attributes_for_merge(self, file_name):
        file = open(file_name)
        file_dict = json.load(file)
        file_keys = list(file_dict.keys())
        file_size = len(file_keys)
        file.close()
        return file_dict, file_keys, file_size

    def merge_blocks_2(self, file1, file2, file_destination1, file_destination2):
        # "2019": [3, [[1026857085907226626, 1], [1027004287715553280, 1], [1027005991429332993, 1]]]
        file1_dict, file1_keys, file1_size = self.get_file_attributes_for_merge(file1)
        file2_dict, file2_keys, file2_size = self.get_file_attributes_for_merge(file2)
        total_docs = sum(values[0] for key, values in file1_dict.items())
        total_docs += sum(values[0] for key, values in file2_dict.items())
        threshold = total_docs // 2
        i = j = 0
        contador = 0
        file_destination1_written = False
        merged_dict = dict()
        while i < file1_size and j < file2_size:
            if not file_destination1_written and contador > threshold:
                contador = 0
                file_destination1_written = True
                self.exportar_index(merged_dict, file_destination1)
                merged_dict = dict()
            word_file1 = file1_keys[i]
            word_file2 = file2_keys[j]
            if word_file1 < word_file2:
                contador += file1_dict[word_file1][0]
                merged_dict[word_file1] = file1_dict[word_file1]
                i += 1
            elif word_file1 > word_file2:
                contador += file2_dict[word_file2][0]
                merged_dict[word_file2] = file2_dict[word_file2]
                j += 1
            else:
                contador += file2_dict[word_file2][0] + file1_dict[word_file1][0]
                word1_list = file1_dict[file1_keys[i]]
                word2_list = file2_dict[file2_keys[j]]
                merged_words = list()
                merged_words.append(word1_list[0] + word2_list[0])
                merged_words.append(word1_list[1] + word2_list[1])
                merged_dict[word_file1] = merged_words
                i, j = i + 1, j + 1

        while i < file1_size:
            if file_destination1_written and contador > threshold:
                contador = 0
                file_destination1_written = True
                self.exportar_index(merged_dict, file_destination1)
                merged_dict = dict()
            contador += file1_dict[word_file1][0]
            merged_dict[file1_keys[i]] = file1_dict[file1_keys[i]]
            i += 1
        
        while j < file2_size:
            if file_destination1_written and contador > threshold:
                contador = 0
                file_destination1_written = True
                self.exportar_index(merged_dict, file_destination1)
                merged_dict = dict()
            contador += file2_dict[word_file2][0]
            merged_dict[file2_keys[j]] = file2_dict[file2_keys[j]]
            j += 1

        print(total_docs)
        
        self.exportar_index(merged_dict, file_destination2)


    def get_total_documents(self):
        return self.total_documents


a = Index()

#a.bsb_index_construction("clean", "index")
#print(a.get_total_documents())
a.merge_blocks_2("index/index-tweets_2018-08-07.json","index/index-tweets_2018-08-08.json","index/mergedTest.json", "index/mergedTest2.json")

# hallar document frequency (# de documentos que contienen a t). trivial, tamaño de índice invertido sobre un término
# 