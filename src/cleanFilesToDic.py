import os
import json

input_directory = "clean"

for block in os.listdir(input_directory):
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
            
    
