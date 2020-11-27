import os
import json

def clean_input_files(input_directory="clean"):
    blocks_names = os.listdir(input_directory)
    if blocks_names.count('.DS_Store'):
        blocks_names.remove('.DS_Store')
    for block in blocks_names:
        with open(input_directory + "/" + block) as arrayOfJsons:
            filee = json.load(arrayOfJsons)
            result = dict()
            for tweet in filee:
                body = dict()

                body["userName"] = tweet["user_name"]
                body["body"] = tweet["text"]
                body["date"] = tweet["date"]
                result[tweet["id"]] = body
            with open("clean_likeADict/"+block, 'w') as file:
                file.write(json.dumps(result))
                
        
