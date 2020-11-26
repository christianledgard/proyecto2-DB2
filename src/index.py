# 1) merge
# 2) hallar la norma no sé cómo
# 3) weight tf-idf normalizado
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
import copy

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

        self.total_documents = 0
        self.total_inverted_index_documents = 1037642
        self.inverted_index_documents_per_block = 16213

        self.file_name_counter = 0

        # bsb
        self.bsb_index_construction(input_directory, index_directory)

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
                pre_procesado = self.pre_procesamiento(item["text"])
                grupos_de_palabras_con_id[item["id"]] = pre_procesado
                grupos_de_palabras.append(pre_procesado)
        return self.generar_index(grupos_de_palabras_con_id, self.dic_palabras_con_terminos_mas_frecuentes(grupos_de_palabras))

    def bsb_index_construction(self, input_directory, output_directory):
        """
        for block in os.listdir(input_directory):
            index = self.procesar_index(input_directory + "/" + block)
            self.exportar_index(index, output_directory + "/index-" + block)
        self.generate_index_blocks(self.index_directory, self.total_desired_blocks, self.merge_directory)
            """
        self.merge_all_blocks(self.merge_directory, self.sorted_blocks_directory)

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
                input_directory = merge_directory
                output_directory = sorted_blocks_directory
            else:
                input_directory = sorted_blocks_directory
                output_directory = merge_directory

            while len(blocks_names_copy) > 0: # while there exist copies in the current iteration (L)
                # get input blocks names
                input_blocks1 = copy.deepcopy(list(blocks_names_copy[:total_blocks_to_compare]))
                del blocks_names_copy[:total_blocks_to_compare]
                input_blocks2 = copy.deepcopy(list(blocks_names_copy[:total_blocks_to_compare]))
                del blocks_names_copy[:total_blocks_to_compare]
                # declare output block
                output = dict()
                current_block_size = 0
                # declare input blocks
                input1 = dict(json.load(open(input_directory + '/' + input_blocks1.pop(0))))
                input2 = dict(json.load(open(input_directory + '/' + input_blocks2.pop(0))))

                self.file_name_counter = 0

                input1_sum = sum(values[0] for key, values in input1.items())
                input2_sum = sum(values[0] for key, values in input2.items())
                
                while True:
                    term1 = pop_first_item_from_dict(input1)
                    term2 = pop_first_item_from_dict(input2)

                    if term1 < term2:
                        current_block_size += term1[1][0]
                        self.update_block(term1, output)
                    elif term1 > term2:
                        current_block_size += term2[1][0]
                        self.update_block(term2, output)
                    else:
                        current_block_size += term1[1][0] + term2[1][0]
                        self.update_block(term1, output)
                        self.update_block(term2, output)

                    last_block = self.file_name_counter > 0 and (self.file_name_counter + 1) % (total_blocks_to_compare * 2) == 0

                    if not last_block and current_block_size >= self.inverted_index_documents_per_block:
                        self.write_index_and_update_file_counter(output, output_directory, self.file_name_counter)

                    if not self.check_and_update_inputs(input1, input_blocks1) or not self.check_and_update_inputs(input2, input_blocks2):
                        output_sum = sum(values[0] for key, values in output.items())
                        p = 0
                        break

                # write remaining inputs
                self.update_block_with_remaining_inputs(input_blocks1, input1, current_block_size, output, output_directory, self.file_name_counter, total_blocks_to_compare)
                self.update_block_with_remaining_inputs(input_blocks2, input2, current_block_size, output, output_directory, self.file_name_counter, total_blocks_to_compare)

                # write last block of current input group
                self.write_index_and_update_file_counter(output, output_directory, self.file_name_counter)

            total_blocks_to_compare *= 2

        if total_iterations % 2 == 0:
            for block_name in blocks_names:
                block = dict(json.load(open(merge_directory + '/' + block_name)))
                self.exportar_index(block, sorted_blocks_directory + '/' + block_name)
        # done

    def write_index_and_update_file_counter(self, output, output_directory, file_name_counter):
        self.exportar_index(output, output_directory + "/" + str(self.file_name_counter) + '.json')
        output = dict()
        self.file_name_counter += 1

    def check_and_update_inputs(self, current_input, input_blocks):
        if len(current_input) == 0:
            if len(input_blocks) > 0:
                current_input = input_blocks.pop(0)
            else:
                return False
        return True

    def update_block_with_remaining_inputs(self, input_blocks, current_input, current_block_size, output, directory, file_name_counter, total_blocks_to_compare):
        while len(input_blocks) > 0 or len(current_input) > 0:
            term = pop_first_item_from_dict(current_input)
            self.update_block(term, output)
            current_block_size += term[1][0]
            last_block = self.file_name_counter > 0 and (self.file_name_counter + 1) % (total_blocks_to_compare * 2) == 0
            if not last_block and current_block_size >= self.inverted_index_documents_per_block:
                self.write_index_and_update_file_counter(output, directory, self.file_name_counter)
            if not self.check_and_update_inputs(current_input, input_blocks):
                break

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
    term = copy.deepcopy(list(dictionary.items())[0])
    del dictionary[term[0]]
    return term

a = Index("clean", "inverted_index", "merging_blocks", "sorted_blocks", 64)


def test():
    print("hola")

#a.bsb_index_construction("clean", "index")
#a.merge_blocks("index/")
#a.merge_blocks_2("index/index-tweets_2018-08-07.json","index/index-tweets_2018-08-08.json","index/mergedTest.json", "index/mergedTest2.json")

#a.generate_index_blocks("inverted_index", 64, "merging_blocks")
#a.merge_all_blocks("merging_blocks")

# hallar document frequency (# de documentos que contienen a t). trivial, tamaño de índice invertido sobre un término
# 