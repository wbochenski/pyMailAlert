from pathlib import Path
from typing import List, Dict, Any
import configparser
import pandas as pd
from datetime import datetime
import re
import ast

def read_ini(path: Path) -> Dict[str, Dict[str, str]]:
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
    section: Dict[str, str] = ini[section_name]
    location: Path = Path(section["location"])
    condition: str = section["condition"]
    result: List[str] = str_to_list(section["result"])
    files: List[Path] = get_list_of_files_matching_path(location)
    result_df: pd.DataFrame = pd.DataFrame()

    for file in files:
        df: pd.DataFrame = pd.read_csv(str(file))

        if result == []:
            df = df.query(condition).reset_index(drop=True)
        else:
            df = df.query(condition)[result].reset_index(drop=True)

        result_df = pd.concat([result_df, df], ignore_index=True)
    
    if "template_path" in section:
        template_path: Path = Path(section["template_path"])
    else:
        template_path: Path = Path(ini["config"]["template_path"])

    with open(template_path, "r") as files:
        template_content: str = files.read()
        final_content: str = re.sub(r'\[result\]', result_df.to_string(index=False), template_content)

        file_name: Path = Path(str(section_name) + "-" + str(datetime.today().strftime('%Y-%m-%d')) + ".html")
        folder_name: Path = get_list_of_files_matching_path(Path(ini["config"]["mail_folder"]).resolve() / \
                                                      Path(f"[[]{ini[section_name]["mail_to"]}[]]*"))[0]

        with open(folder_name / file_name, "w") as mail:
            mail.write(final_content)

ini = read_ini(Path("test.ini"))

for section_name in ini:
    if section_name == "config": continue

    if ini[section_name]["type"] == "csv":
        do_csv(ini, section_name)
    elif ini[section_name]["type"] == "xlsx":
        pass
    elif ini[section_name]["type"] == "sql":
        pass
