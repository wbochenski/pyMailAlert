from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime
import re

def ReadINI(path: Path) -> dict:
    import configparser
    
    ini = {}

    config = configparser.ConfigParser()
    config.read(path)

    for i in config:
        if i == "DEFAULT": continue
        ini[i] = {}
        for j in config[i]:
            ini[i][j] = str(config[i][j])
    
    return ini
def GetMatchingFiles(path: Path) -> List:
    from glob import escape

    path = Path(path)
    es = path.name
    return [p for p in path.parent.glob(es)]

# def SubstitutePartsOfQuery(query: str) -> str:
#     Log(f"Substitute query ({query})")

#     def SubstituteFunction(query: str) -> str:
#         for function in FUNCTIONS:

#             regularExpression = re.sub(r'\(', r'\\(', function)
#             regularExpression = re.sub(r'\)', r'\\)', regularExpression)
#             regularExpression = re.sub(r'\$(\d+)', r'(\\S+)', regularExpression)

#             pattern = re.compile(regularExpression)

#             def ReplaceFunction(match):
#                 def ReplaceParameters(match2):
#                     parameter_value = int(match2.group(1))
#                     return str(match.group(parameter_value))  
#                 return re.sub(r'\$(\d+)', ReplaceParameters, FUNCTIONS[function])

#             new_query = re.sub(pattern, ReplaceFunction, query)

#             if query != new_query:
#                 return new_query
#         return query
    
#     def SubstituteArguments(query: str) -> str:
#         args = GetArguments()
#         return re.sub(r'@([a-zA-Z_][a-zA-Z0-9_]*)', lambda match: args.get(match.group(1), f"@{match.group(1)}"), query)
    
#     new_query = SubstituteArguments(SubstituteFunction(query))

#     Log(f"Query ({query}) substitiuted ({new_query})")
#     return new_query

ini = ReadINI(Path("test.ini"))

for section in ini:
    if section == "config": continue

    if ini[section]["type"] == "csv":
        files = GetMatchingFiles(ini[section]["location"])
        gigadf=pd.DataFrame()
        for file in files:
            table = pd.read_csv(file)
            if ini[section]["result"] == "[]":
                exec(f"table = table[{ini[section]["condition"]}].reset_index(drop=True)")
            else:
                exec(f"table = table[{ini[section]["condition"]}][{ini[section]["result"]}].reset_index(drop=True)")
            gigadf = pd.concat([gigadf, table], ignore_index=True)
        
        if "template_path" in ini[section]:
            template_path = ini[section]["template_path"]
        else:
            template_path = ini["config"]["template_path"]

        with open(template_path, "r") as file:

            text = file.read()
            text2 = re.sub(r'\[result\]', gigadf.to_string(index=False), text)
            filename = Path(str(section) + "-" + str(datetime.today().strftime('%Y-%m-%d')) + ".html")
            pathfolder = Path(ini["config"]["mail_folder"]).resolve() / Path(f"[[]{ini[section]["mail_to"]}[]]*")
            essa = GetMatchingFiles(pathfolder)
            if len(essa) != 1:
                print("BLAD")
            essa = essa[0]
            with open(essa / filename, "w") as file2:
                file2.write(text2)
        

    elif ini[section]["type"] == "xlsx":
        pass
    elif ini[section]["type"] == "sql":
        pass
