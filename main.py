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

def df_to_html(df: pd.DataFrame) -> str:
    """Changes pandas DataFrame to html table"""
    unique_files = df["file"].unique()
    table = "<table>"

    for file in unique_files:
        df_filtered = df[df["file"] == file]
        df_filtered = df_filtered.drop(columns=['file'])

        table += f'<tr><td colspan="{len(df_filtered.columns)}">{file}</td></tr>'

        table += "<tr>"
        for column_name in df_filtered.columns:
            table += f"<td>{column_name}</td>"
        table += "</tr>"

        for _, row in df_filtered.iterrows():
            table += "<tr>"
            for row_element in row:
                table += f"<td>{row_element}</td>"
            table += "</tr>"
    table += "</table>"

    return table

def check_text_files(ini: Dict[str, Dict[str, str]], section_name: str) -> None:
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
        df_filtered["file"] = file
        result = pd.concat([result, df_filtered], ignore_index=True)

    if not result.empty:
        template = read_template(ini, section_name)
        content = re.sub(r'\[result\]', df_to_html(result), template)
        send_mail(ini, section_name, content)

def read_template(ini: Dict[str, Dict[str, str]], section_name: str) -> str:
    """Read template from a file depending if template_path was given to section if not the global one is taken"""
    section = ini[section_name]
    template_path = Path(section.get("template_path", ini["config"]["template_path"]))
    with open(template_path, "r") as template_file:
        template = template_file.read()

    return template 

def send_mail(ini: Dict[str, Dict[str, str]], section_name: str, content: str) -> None:
    """Adds content to a folder matching id with a proper file name"""
    reciepents = str_to_list(ini[section_name]["mail_to"])
    for i in reciepents:
        file_name = f"{section_name}-{datetime.today().strftime('%Y-%m-%d')}.html"
        folder_name = get_files_matching_path(Path(ini["config"]["mail_folder"]) / 
                                            Path(f"[[]{i}[]]*"))[0]

        with open(folder_name / file_name, "w") as mail:
            mail.write(content)

def main(ini_path: Union[Path, str]) -> None:
    """Process all sections in the INI file."""
    ini = read_ini(ini_path)

    for section_name in ini:
        if section_name == "config":
            continue
        if ini[section_name]["type"] in {"csv", "xlsx"}:
            check_text_files(ini, section_name)

if __name__ == "__main__":
    main("test.ini")