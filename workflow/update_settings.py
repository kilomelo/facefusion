import configparser
import os
from tqdm import tqdm

def update_config(file_path, updates):
    """
    更新 .ini 配置文件中的指定键值对。

    :param file_path: 配置文件的路径。
    :param updates: 一个列表，其中包含 (key, value) 元组。
    """
    # 初始化配置解析器
    config = configparser.ConfigParser()
    
    if not os.path.isfile(file_path):
        tqdm.write(f"File {file_path} not found.")
        return
    # 读取现有的配置文件
    config.read(file_path)
    
    # 遍历更新列表，更新配置值
    for section, key, value in updates:
        if config.has_section(section) and config.has_option(section, key):
            config.set(section, key, value)
        else:
            tqdm.write(f"Section {section} or key {key} not found in {file_path}")
            tqdm.write("Current configuration sections and keys:")
            for sec in config.sections():
                tqdm.write(f"Section: {sec}")
                for k in config[sec]:
                    tqdm.write(f"  Key: {k} -> Value: {config[sec][k]}")
    
    # 将更新后的配置写回文件
    with open(file_path, 'w') as configfile:
        config.write(configfile)
    # tqdm.write("Configuration updated successfully.")