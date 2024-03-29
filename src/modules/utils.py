import os
import sys
import json
import pickle
import pandas as pd

project_path = os.getenv('project_path')


def get_config(module_name):
    with open(f'{project_path}/src/configs/{module_name}Config.json', 'r') as file:
        config = json.load(file)
    return config


def get_data(file_name, sub_dir=''):
    data_dir_path = f'{project_path}/data'
    full_dir_path = data_dir_path if sub_dir == '' else f"{data_dir_path}/{sub_dir}"
    file_path = f"{full_dir_path}/{file_name}"
    
    if not os.path.exists(file_path):
        print(f"error: file '{file_path}' not exist", file=sys.stderr)
        return None
    
    if '.csv' in file_name:
        data = pd.read_csv(file_path)
    elif '.pickle' in file_name:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
    else:
        print(f"error: unsupported file extension {file_name.split('.')[-1]} for saving data", file=sys.stderr)
        return None
    return data


def save_data(data, file_name, sub_dir=''):
    data_dir_path = f'{project_path}/data'
    full_dir_path = data_dir_path if sub_dir == '' else f"{data_dir_path}/{sub_dir}"
    file_path = f"{full_dir_path}/{file_name}"

    if not os.path.isdir(data_dir_path):
        os.mkdir(data_dir_path)
    if not os.path.isdir(full_dir_path):
        os.mkdir(full_dir_path)

    if '.csv' in file_name:
        data.to_csv(file_path, index=False)
    elif '.pickle' in file_name:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    else:
        print(f"error: unsupported file extension {file_name.split('.')[-1]} for saving data", file=sys.stderr)
        return False
    return True
