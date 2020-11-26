import os
import json

input_directory = "clean_likeADict"

def mapping_from_id_to_result(dic_of_ids):
    number = 0
    result = dict()
    for block in os.listdir(input_directory):
        with open(input_directory + "/" + block) as arrayOfJsons:
            archivo = json.load(arrayOfJsons)
            for key, value in dic_of_ids.items():
                for tweet_id in archivo:
                    if tweet_id == key:
                        result[number] = archivo[tweet_id]
                        number+=1
    print(result)
                
                

dic_of_ids = {"1027057888706084864":1,"1033581001325400064":2,"1041552421200293891":3,"1041552548539322369":4}
mapping_from_id_to_result(dic_of_ids)