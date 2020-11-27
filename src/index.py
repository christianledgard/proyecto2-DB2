# 4) consulta
#   4a) cargar índice
#   4b) hacer consulta
#   4c) mostrar resultados

import nltk
from operator import itemgetter
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import json
import math
import os
import sys
import copy
from cleanFilesToDic import clean_input_files

nltk.download('punkt')
nltk.download('stopwords')
stemmer = SnowballStemmer('spanish')

class Index:

    def __init__(self, input_directory, index_directory, merge_directory, sorted_blocks_directory, total_desired_blocks):
        self.input_directory = input_directory
        self.index_directory = index_directory
        self.merge_directory = merge_directory
        self.sorted_blocks_directory = sorted_blocks_directory
        self.total_desired_blocks = total_desired_blocks

        self.total_documents = 0 # 78127
        self.total_inverted_index_documents = 0 # 1037642
        self.inverted_index_documents_per_block = 0 # 16213

        self.file_name_counter = 0
        self.current_block_size = 0
        self.output = dict() # output block

        # bsbi
        self.bsb_index_construction(input_directory, index_directory)

        # export metadata
        self.export_metedata()

        # hallar norma e tf-idf
        self.calculate_tf_idf(self.sorted_blocks_directory) 

    """
    def calculate_tf_idf(self, directory, clean_directory="clean_likeADict"):
        #"hagamosl": [df: 2, [[1038525060129148928, tf: 1, tf-idf], [1038525060129148928, tf: 1, tf-idf]]]
        # tf-idf = log10(1 + tf) * log10(total_documents / df)
        clean_input_files()
        blocks_names = list(sorted(os.listdir(directory)))
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        blocks_names = sorted(blocks_names, key=sort_file_names)
        for block_name in blocks_names:
            block = dict(json.load(open(directory + "/" + block_name)))
            for key, value in block.items():
                idf = math.log10(self.total_documents / int(value[0]))
                for tweet in value[1]:
                    tf = math.log10(1 + tweet[1])
                    tf_idf = tf * idf
                    if len(tweet) <= 2:
                        tweet.append(tf_idf)
                    else:
                        tweet[2] = tf_idf
                    
                    documents_blocks_names = list(sorted(os.listdir(clean_directory)))
                    if documents_blocks_names.count('.DS_Store'):
                        documents_blocks_names.remove('.DS_Store')
                    for documents_block_name in documents_blocks_names:
                        document_block = dict(json.load(open(clean_directory + "/" + documents_block_name)))
                        if str(tweet[0]) in document_block:
                            if "squared_tf_idf" not in document_block[str(tweet[0])]:
                                document_block[str(tweet[0])]["squared_tf_idf"] = math.pow(tf_idf, 2)
                            else:
                                document_block[str(tweet[0])]["squared_tf_idf"] += math.pow(tf_idf, 2)
                            self.exportar_index(document_block, clean_directory + "/" + documents_block_name)
                            break

            self.exportar_index(block, directory + "/" + block_name)
            """

    # norma
    def calculate_tf_idf(self, directory, clean_directory="clean_likeADict"):
        #"hagamosl": [df: 2, [[1038525060129148928, tf: 1, tf-idf], [1038525060129148928, tf: 1, tf-idf]]]
        # tf-idf = log10(1 + tf) * log10(total_documents / df)
        clean_input_files()
        blocks_names = list(sorted(os.listdir(directory)))
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        blocks_names = sorted(blocks_names, key=sort_file_names)
        documents_squared_tf_idf = dict()
        for block_name in blocks_names:
            block = dict(json.load(open(directory + "/" + block_name)))
            for key, value in block.items():
                idf = math.log10(self.total_documents / int(value[0]))
                for tweet in value[1]:
                    tf = math.log10(1 + tweet[1])
                    tf_idf = tf * idf
                    if len(tweet) <= 2:
                        tweet.append(tf_idf)
                    else:
                        tweet[2] = tf_idf
                    
                    if str(tweet[0]) not in documents_squared_tf_idf:
                        documents_squared_tf_idf[str(tweet[0])] = math.pow(tf_idf, 2)
                    else:
                        documents_squared_tf_idf[str(tweet[0])] += math.pow(tf_idf, 2)

            self.exportar_index(block, directory + "/" + block_name)

        for key, value in documents_squared_tf_idf.items():
            documents_squared_tf_idf[key] = math.sqrt(value)
        self.exportar_index(documents_squared_tf_idf, "documents_norm.json")

    def calculate_sqrt_tf_idf(self, directory):
        blocks_names = list(sorted(os.listdir(directory)))
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        blocks_names = sorted(blocks_names, key=sort_file_names)
        for block_name in blocks_names:
            block = dict(json.load(open(directory + "/" + block_name)))
            for key, value in block.items():
                block[key]["tf_idf"] = math.sqrt(block[key]["squared_tf_idf"])
            self.exportar_index(block, directory + "/" + block_name)


    def export_metedata(self):
        result = dict()
        result["totalDocuments"] = self.total_documents
        self.exportar_index(result, "metadata.json")

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
        return frecuencia_palabras

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
                pre_procesado = pre_procesamiento(item["text"])
                grupos_de_palabras_con_id[item["id"]] = pre_procesado
                grupos_de_palabras.append(pre_procesado)
        return self.generar_index(grupos_de_palabras_con_id, self.dic_palabras_con_terminos_mas_frecuentes(grupos_de_palabras))

    def bsb_index_construction(self, input_directory, output_directory):
        blocks_names = os.listdir(input_directory)
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        for block in blocks_names:
            index = self.procesar_index(input_directory + "/" + block)
            self.exportar_index(index, output_directory + "/index-" + block)
    
        self.generate_index_blocks(self.index_directory, self.total_desired_blocks, self.merge_directory)
        self.merge_all_blocks(self.merge_directory, self.sorted_blocks_directory)
        
    def get_file_metadata(self, file_name):
        file = open(file_name)
        file_dict = json.load(file)
        file_keys = list(file_dict.keys())
        file_size = len(file_keys)
        file.close()
        return file_dict, file_keys, file_size

    def merge_all_blocks(self, merge_directory, sorted_blocks_directory):
        blocks_names = (list(os.listdir(merge_directory)))
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        blocks_names = sorted(blocks_names, key=sort_file_names)
        output_file_names = copy.deepcopy(list(blocks_names))
        total_iterations = int(math.log2(len(blocks_names)))
        
        total_blocks_to_compare = 1
        for i in range(total_iterations): # total iterations to get the result
            blocks_names_copy = copy.deepcopy(list(blocks_names))

            if i % 2 == 0:
                self.input_directory = merge_directory
                output_directory = sorted_blocks_directory
            else:
                self.input_directory = sorted_blocks_directory
                output_directory = merge_directory

            self.file_name_counter = 0

            while len(blocks_names_copy) > 0: # while there exist copies in the current iteration (L)
                # get input blocks names
                input_blocks1 = copy.deepcopy(list(blocks_names_copy[:total_blocks_to_compare]))
                del blocks_names_copy[:total_blocks_to_compare]
                input_blocks2 = copy.deepcopy(list(blocks_names_copy[:total_blocks_to_compare]))
                del blocks_names_copy[:total_blocks_to_compare]
                # declare self.output block
                self.output = dict()
                self.current_block_size = 0
                # declare input blocks
                input1 = list(dict(json.load(open(self.input_directory + '/' + input_blocks1.pop(0)))).items())
                input2 = list(dict(json.load(open(self.input_directory + '/' + input_blocks2.pop(0)))).items())

                while True:

                    term1 = input1[0]
                    term2 = input2[0]

                    if term1[0] < term2[0]:
                        self.current_block_size += term1[1][0]
                        self.update_block(term1, self.output)
                        input1.pop(0)
                    elif term1[0] > term2[0]:
                        self.current_block_size += term2[1][0]
                        self.update_block(term2, self.output)
                        input2.pop(0)
                    else:
                        self.current_block_size += (term1[1][0] + term2[1][0])
                        self.update_block(term1, self.output)
                        self.update_block(term2, self.output)
                        input1.pop(0)
                        input2.pop(0)

                    last_block = self.file_name_counter > 0 and (self.file_name_counter + 1) % (total_blocks_to_compare * 2) == 0

                    if not last_block and self.current_block_size >= self.inverted_index_documents_per_block:
                        self.write_index_and_update_file_counter(self.output, output_directory, self.file_name_counter)

                    # check if an input is empty
                    if len(input1) == 0:
                        if len(input_blocks1) > 0: 
                            input1 = list(dict(json.load(open(self.input_directory + '/' + input_blocks1.pop(0)))).items()) 
                        else: break
                    if len(input2) == 0:
                        if len(input_blocks2) > 0:
                            input2 = list(dict(json.load(open(self.input_directory + '/' + input_blocks2.pop(0)))).items()) 
                        else: break

                # write remaining inputs
                self.update_block_with_remaining_inputs(input_blocks1, input1, self.current_block_size, self.output, output_directory, self.file_name_counter, total_blocks_to_compare)
                self.update_block_with_remaining_inputs(input_blocks2, input2, self.current_block_size, self.output, output_directory, self.file_name_counter, total_blocks_to_compare)

                # write last block of current input group
                self.write_index_and_update_file_counter(self.output, output_directory, self.file_name_counter)

            total_blocks_to_compare *= 2

        if total_iterations % 2 == 0:
            for block_name in blocks_names:
                block = dict(json.load(open(merge_directory + '/' + block_name)))
                self.exportar_index(block, sorted_blocks_directory + '/' + block_name)

    def write_index_and_update_file_counter(self, output, output_directory, file_name_counter):
        self.exportar_index(self.output, output_directory + "/" + str(self.file_name_counter) + '.json')
        self.output = dict()
        self.file_name_counter += 1
        self.current_block_size = 0

    def update_block_with_remaining_inputs(self, input_blocks, current_input, current_block_size, output, directory, file_name_counter, total_blocks_to_compare):
        while len(input_blocks) > 0 or len(current_input) > 0:
            term = current_input.pop(0) #Cambie de pop_first_item_from_dict a
            self.update_block(term, self.output)
            self.current_block_size += term[1][0]
            last_block = self.file_name_counter > 0 and (self.file_name_counter + 1) % (total_blocks_to_compare * 2) == 0
            if not last_block and self.current_block_size >= self.inverted_index_documents_per_block:
                self.write_index_and_update_file_counter(self.output, directory, self.file_name_counter)
            if len(current_input) == 0:
                if len(input_blocks) > 0: 
                    current_input = list(dict(json.load(open(self.input_directory + '/' + input_blocks.pop(0)))).items()) 
                else: break

    def get_total_documents(self):
        return self.total_documents

    def update_block(self, term, block):
        if term[0] not in block:
            block[term[0]] = term[1]
        else:
            term_to_update = copy.deepcopy(block[term[0]])
            term_to_update[0] += term[1][0]
            for doc in block[term[0]][1]:
                term_to_update[1].append(doc)
            block[term[0]] = term_to_update

    def generate_index_blocks(self, index_directory, total_desired_blocks, merge_directory):
        if not is_power(total_desired_blocks, 2):
            raise Exception("Sorry, not a valid number of blocks")

        self.total_inverted_index_documents = 0
        index_files = list(os.listdir(index_directory))

        if index_files.count('.DS_Store'):
            index_files.remove('.DS_Store')

        for index_file in index_files:
            index_file_dict = self.get_file_metadata(index_directory + "/" + index_file)[0]
            self.total_inverted_index_documents += sum(values[0] for key, values in index_file_dict.items())
        
        self.inverted_index_documents_per_block = self.total_inverted_index_documents // total_desired_blocks
    
        current_block = dict()
        current_index_file = dict(json.load(open(index_directory + "/" + index_files.pop())))

        for i in range(total_desired_blocks):
            if i == total_desired_blocks - 1:
                while len(current_index_file) > 0:
                    current_term = current_index_file.popitem()
                    self.update_block(current_term, current_block)
            else:
                total_block_documents = 0
                while total_block_documents < self.inverted_index_documents_per_block:
                    current_term = copy.deepcopy(list(current_index_file.popitem()))
                    if current_term[1][0] + total_block_documents > self.inverted_index_documents_per_block:
                        available_spots = self.inverted_index_documents_per_block - total_block_documents
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
                        self.update_block(to_insert_to_block, current_block)
                    else:
                        self.update_block(current_term, current_block)
                    total_block_documents += current_term[1][0]
                    if len(current_index_file) == 0:
                        current_index_file = dict(json.load(open(index_directory + "/" + index_files.pop())))
            self.exportar_index(dict(sorted(current_block.items())), merge_directory + "/" + str(i) + '.json')
            current_block = dict()

class Query:
    def query(self, words, K):
        blocks_names = os.listdir("sorted_blocks") # dir is your directory path
        if blocks_names.count('.DS_Store'):
            blocks_names.remove('.DS_Store')
        blocks_names = sorted(blocks_names, key=sort_file_names)
        key_words=[]
        for block_name in blocks_names:
            block = list(json.load(open("sorted_blocks/" + block_name)))
            key_words.append([block.pop(0), block.pop()])

        pre_processed = pre_procesamiento(words)

        N = dict(json.load(open("metadata.json")))["totalDocuments"]
        data = []

        for key, value in dict(json.load(open("documents_norm.json"))).items():
            data.append([key, sys.maxsize , value])

        ids = {}
        for i in range(len(data)):
            ids[data[i][0]] = i

        for word in pre_processed:
            bs = self.search(word,(key_words)) #Retorna [bool, lista de Documentos que la contienen]
            if(bs[0]!=False):
                for it in bs[1]:
                    if(data[ids[it]][1]== sys.maxsize):
                        data[ids[it]][1]=0
                    data[ids[it]][1]+=it[2]
            
        for i in range(len(data)):
            data[i][1]=data[i][1]/data[i][2]
        data = sorted(data, key=itemgetter(1),reverse=False)
        data= data[:int(K)]


        clean_directory_files = os.listdir("clean_likeADict")
        if clean_directory_files.count(".DS_Store"):
            clean_directory_files.remove(".DS_Store")

        tweets_info = []
        for doc in data:
            for filename in clean_directory_files:
                f = dict(json.load(open("clean_likeADict/" + filename)))
                if doc[0] in f:
                    tweets_info.append(f[doc[0]]['body'])
                    break

        for x in tweets_info:
            print(x,end="\n\n\n")
        return tweets_info


    def search(self,palabra,key_words):
        bloque = self.search_bloque(palabra,key_words)
        if(bloque==None):
            return [False] * 2
        
        bloque_cargado = list(json.load(open("sorted_blocks/" + str(bloque) + '.json')))
        #bloque=lista cargada desde json
        return self.binary_search_block(bloque_cargado,palabra)

    def search_bloque(self, palabra,key_words):
        for i in range(len(key_words)):
            if key_words[i][0] <= palabra and key_words[i][1] >= palabra:
                return i
        return None

    def binary_search_block(self, lista, palabra):
        if len(lista) == 1:
            return [lista[0][0] == palabra, lista[0][1]]

        middle = len(lista)//2
        if lista[middle][0] == palabra:
            return True, lista[middle][1]
        elif palabra < lista[middle] :
            return self.binary_search_block(lista[:middle], palabra)
        else:
            return self.binary_search_block(lista[middle:], palabra)


def is_power (num, base):
    if base in {0, 1}:
        return num == base
    testnum = base
    while testnum < num:
        testnum = testnum * base
    return testnum == num

def sort_file_names(file_name):
    s = file_name.split('.')
    return int(s[0])

def pop_first_item_from_dict(dictionary):
    term = copy.deepcopy(list(list(dictionary.items())[0]))
    del dictionary[term[0]]
    return term


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

a = Index("clean", "inverted_index", "merging_blocks", "sorted_blocks", 16)

#a.bsb_index_construction("clean", "index")
#a.merge_blocks("index/")
#a.merge_blocks_2("index/index-tweets_2018-08-07.json","index/index-tweets_2018-08-08.json","index/mergedTest.json", "index/mergedTest2.json")

#a.generate_index_blocks("inverted_index", 64, "merging_blocks")
#a.merge_all_blocks("merging_blocks")

# hallar document frequency (# de documentos que contienen a t). trivial, tamaño de índice invertido sobre un término
# 