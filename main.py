from pathlib import Path
from typing import List, Dict
import configparser
import pandas as pd
from datetime import datetime
import re
import ast

def read_ini(path: Path|str) -> Dict[str, Dict[str, str]]:
    ini: Dict[str, Dict[str, str]] = {}

    config = configparser.ConfigParser()
    config.read(path)

    for section in config:
        if section == "DEFAULT": 
            continue
        ini[section] = {}
        for key in config[section]:
            ini[section][key] = str(config[section][key])
    
    return ini

def str_to_list(input: str) -> List:
    return ast.literal_eval(input)

def get_list_of_files_matching_path(path: Path) -> List[Path]:
    path = Path(path)
    files: List[Path] = [p for p in path.parent.glob(path.name)]
    return files

def do_csv(ini: Dict[str, dict[str, str]], section_name: str) -> None:
    section = ini[section_name]
    location = Path(section["location"])
    condition = section["condition"]
    result = str_to_list(section["result"])
    files = get_list_of_files_matching_path(location)
    result_df = pd.DataFrame()

    for file in files:
        df = pd.read_csv(str(file))

        if result == []:
            df = df.query(condition).reset_index(drop=True)
        else:
            df = df.query(condition)[result].reset_index(drop=True)

        result_df = pd.concat([result_df, df], ignore_index=True)
    
    if "template_path" in section:
        template_path = Path(section["template_path"])
    else:
        template_path = Path(ini["config"]["template_path"])

    with open(template_path, "r") as template:
        template_content = template.read()
        final_content = re.sub(r'\[result\]', result_df.to_string(index=False), template_content)

        file_name = Path(str(section_name) + "-" + str(datetime.today().strftime('%Y-%m-%d')) + ".html")
        folder_name = get_list_of_files_matching_path(Path(ini["config"]["mail_folder"]).resolve() / \
                                                      Path(f"[[]{ini[section_name]["mail_to"]}[]]*"))[0]

        with open(folder_name / file_name, "w") as mail:
            mail.write(final_content)


def do_excel(ini: Dict[str, dict[str, str]], section_name: str) -> None:
    section = ini[section_name]
    location = Path(section["location"])
    condition = section["condition"]
    result = str_to_list(section["result"])
    files = get_list_of_files_matching_path(location)
    result_df = pd.DataFrame()

    for file in files:
        df = pd.read_excel(file)

        if result == []:
            df = df.query(condition).reset_index(drop=True)
        else:
            df = df.query(condition)[result].reset_index(drop=True)

        result_df = pd.concat([result_df, df], ignore_index=True)
    
    if "template_path" in section:
        template_path = Path(section["template_path"])
    else:
        template_path = Path(ini["config"]["template_path"])

    with open(template_path, "r") as template:
        template_content = template.read()
        final_content = re.sub(r'\[result\]', result_df.to_string(index=False), template_content)

        file_name = Path(str(section_name) + "-" + str(datetime.today().strftime('%Y-%m-%d')) + ".html")
        folder_name = get_list_of_files_matching_path(Path(ini["config"]["mail_folder"]).resolve() / \
                                                      Path(f"[[]{ini[section_name]["mail_to"]}[]]*"))[0]

        with open(folder_name / file_name, "w") as mail:
            mail.write(final_content)

ini = read_ini("test.ini")

for section_name in ini:
    if section_name == "config": continue

    if ini[section_name]["type"] == "csv":
        do_csv(ini, section_name)
    elif ini[section_name]["type"] == "xlsx":
        do_excel(ini, section_name)
    elif ini[section_name]["type"] == "sql":
        pass
