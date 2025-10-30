from configparser import ConfigParser
import os
from typing import Dict, Any


def config(filename: str = "database.ini", section: str = "postgresql") -> Dict[str, Any]:

    current_dir = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.normpath(os.path.join(current_dir, '..', filename))
    #print("Путь к файлу конфигурации:", full_path)
    parser = ConfigParser()
    with open(full_path, 'r', encoding='utf-8') as f:
        parser.read_file(f)
    #print(f"Sections in config: {parser.sections()}")
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db