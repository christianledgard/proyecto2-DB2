import nltk
from operator import itemgetter
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import json
import math
import os
import copy

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


    def merge_all_blocks(self, merge_directory):
        blocks = os.listdir(merge_directory)
        total_iterations = len(blocks)
        print(blocks)
        print(total_iterations)

    def merge_blocks(self, directory):
        destination_path = directory + "primeraPasada"

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
    
        files = sorted(os.listdir(directory))[1:]
        for i in range(0, len(files), 2):
            print(directory + files[i], " - ", directory + files[i+1])
            self.merge_blocks_2(directory + files[i], directory + files[i+1], destination_path+"/"+str(i)+".json", destination_path+"/"+str(i+1)+".json")
        

    def get_file_metadata(self, file_name):
        file = open(file_name)
        file_dict = json.load(file)
        file_keys = list(file_dict.keys())
        file_size = len(file_keys)
        file.close()
        return file_dict, file_keys, file_size

    def merge_blocks_2(self, file1, file2, file_destination1, file_destination2):
        # "2019": [3, [[1026857085907226626, 1], [1027004287715553280, 1], [1027005991429332993, 1]]]
        file1_dict, file1_keys, file1_size = self.get_file_metadata(file1)
        file2_dict, file2_keys, file2_size = self.get_file_metadata(file2)
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

    def generate_index_blocks(self, index_directory, total_desired_blocks, merge_directory):
        if not is_power(total_desired_blocks, 2):
            raise Exception("Sorry, not a valid number of blocks")
        total_inverted_index_documents = 0
        for index_file in os.listdir(index_directory):
            if index_file != '.DS_Store':
                index_file_dict = self.get_file_metadata(index_directory + "/" + index_file)[0]
                total_inverted_index_documents += sum(values[0] for key, values in index_file_dict.items())
        
        inverted_index_documents_per_block = total_inverted_index_documents // total_desired_blocks
        current_block = dict()
        index_files = list(os.listdir(index_directory))
        current_index_file = dict(json.load(open(index_directory + "/" + index_files.pop())))

        for i in range(total_desired_blocks):
            if i == total_desired_blocks - 1:
                while len(current_index_file) > 0:
                    current_term = current_index_file.popitem()
                    if current_term[0] not in current_block:
                        current_block[current_term[0]] = current_term[1]
                    else:
                        term_to_update = current_block[current_term[0]]
                        term_to_update[0] += current_term[1][0]
                        for doc in term_to_update[1]:
                            term_to_update[1].append(doc)
                        current_block[current_term[0]] = term_to_update
            else:
                total_block_documents = 0
                while total_block_documents < inverted_index_documents_per_block:
                    current_term = copy.deepcopy(list(current_index_file.popitem()))
                    if current_term[1][0] + total_block_documents > inverted_index_documents_per_block:
                        available_spots = inverted_index_documents_per_block - total_block_documents
                        # crear un nuevo elemento solo con los terminos que entran
                        to_insert_to_block = copy.deepcopy(list(current_term))
                        to_insert_to_block[1][0] = available_spots
                        to_insert_to_block[1][1] = current_term[1][1][:available_spots]
                        # actualizar current_index_file
                        to_update = copy.deepcopy(list(current_term))
                        to_update[1][0] = current_term[1][0] - available_spots
                        to_update[1][1] = current_term[1][1][available_spots:]
                        current_index_file[to_update[0]] = to_update[1]
                        # actualizar current_block
                        if to_insert_to_block[0] not in current_block:
                            current_block[to_insert_to_block[0]] = to_insert_to_block[1]
                        else:
                            term_to_update = current_block[to_insert_to_block[0]]
                            term_to_update[0] += to_insert_to_block[1][0]
                            for doc in term_to_update[1]:
                                term_to_update[1].append(doc)
                            current_block[to_insert_to_block[0]] = term_to_update   
                        total_block_documents += current_term[1][0]
                    else:
                        if current_term[0] not in current_block:
                            current_block[current_term[0]] = current_term[1]
                        else:
                            term_to_update = copy.deepcopy(current_block[current_term[0]])
                            term_to_update[0] += current_term[1][0]
                            for doc in current_block[current_term[0]][1]:
                                term_to_update[1].append(doc)
                            current_block[current_term[0]] = term_to_update
                        total_block_documents += current_term[1][0]
                    if len(current_index_file) == 0:
                        current_index_file = dict(json.load(open(index_directory + "/" + index_files.pop())))
            self.exportar_index(current_block, merge_directory + "/" + str(i) + '.json')
            current_block = dict()
        print(len(index_files))



def is_power (num, base):
    if base in {0, 1}:
            return num == base
    testnum = base
    while testnum < num:
        testnum = testnum * base
    return testnum == num

a = Index()

#a.bsb_index_construction("clean", "index")
#print(a.get_total_documents())
#a.merge_blocks("index/")
#a.merge_blocks_2("index/index-tweets_2018-08-07.json","index/index-tweets_2018-08-08.json","index/mergedTest.json", "index/mergedTest2.json")

#a.generate_index_blocks("inverted_index", 64, "merging_blocks")
a.merge_all_blocks("merging_blocks")

# hallar document frequency (# de documentos que contienen a t). trivial, tamaño de índice invertido sobre un término
# 