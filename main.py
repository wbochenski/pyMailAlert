from pathlib import Path
from typing import List, Dict, Union
import configparser
import pandas as pd
from datetime import datetime
import re
import ast

def read_ini(path: Union[Path, str]) -> Dict[str, Dict[str, str]]:
    """Reads an INI file and returns it as a dictionary."""
    ini: Dict[str, Dict[str, str]] = {}
    config = configparser.ConfigParser()
    config.read(path)

    for section in config:
        if section == "DEFAULT": 
            continue
        ini[section] = {key: str(config[section][key]) for key in config[section]}
    
    return ini

def str_to_list(input_str: str) -> List:
    """Converts a string representation of a list into a Python list."""
    try:
        return ast.literal_eval(input_str)
    except ValueError as e:
        raise ValueError(f"Failed to convert string to list: {input_str}") from e

def get_files_matching_path(path: Path) -> List[Path]:
    """Returns a list of files matching the given path pattern."""
    return list(path.parent.glob(path.name))

def load_data(file: Path, file_type: str) -> pd.DataFrame:
    """Loads data from a file based on its type."""
    if file_type == "xlsx":
        return pd.read_excel(file)
    elif file_type == "csv":
        return pd.read_csv(file)
    raise ValueError(f"Unsupported file type: {file_type}")

def apply_condition_and_filter(df: pd.DataFrame, condition: str, result_columns: List[str]) -> pd.DataFrame:
    """Applies a query condition and selects result columns."""
    filtered_df = df.query(condition)
    if result_columns:
        return filtered_df[result_columns].reset_index(drop=True)
    return filtered_df.reset_index(drop=True)

def execute(ini: Dict[str, Dict[str, str]], section_name: str) -> None:
    """Main function to process each section of the INI file."""
    section = ini[section_name]
    file_type = section["type"]
    location = Path(section["location"])
    files = get_files_matching_path(location)
    condition = section["condition"]
    result_columns = str_to_list(section["result"])
    result = pd.DataFrame()

    for file in files:
        df = load_data(file, file_type)
        df_filtered = apply_condition_and_filter(df, condition, result_columns)
        result = pd.concat([result, df_filtered], ignore_index=True)

    template_path = Path(section.get("template_path", ini["config"]["template_path"]))
    with open(template_path, "r") as template:
        template_content = template.read()
        final_content = re.sub(r'\[result\]', result.to_string(index=False), template_content)

    file_name = f"{section_name}-{datetime.today().strftime('%Y-%m-%d')}.html"
    folder_name = get_files_matching_path(Path(ini["config"]["mail_folder"]) / 
                                          Path(f"[[]{ini[section_name]['mail_to']}[]]*"))[0]

    with open(folder_name / file_name, "w") as mail:
        mail.write(final_content)

def main(ini_path: Union[Path, str]) -> None:
    """Process all sections in the INI file."""
    ini = read_ini(ini_path)

    for section_name in ini:
        if section_name == "config":
            continue
        if ini[section_name]["type"] in {"csv", "xlsx"}:
            execute(ini, section_name)

if __name__ == "__main__":
    main("test.ini")