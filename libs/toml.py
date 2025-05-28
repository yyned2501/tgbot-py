import os
import toml
import tomllib


def toml_read_state(file_path) -> dict:
    """读取toml文件
    Returns:
        dict: 数据
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "rb") as f:
        return tomllib.load(f)


def toml_write_state(data: dict, file_path) -> None:
    """吸入toml文件
    Args:
        data (dict): 数据
    """
    with open(file_path, "w") as f:
        toml.dump(data, f)
