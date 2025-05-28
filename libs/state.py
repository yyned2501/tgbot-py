from libs import toml

PATH = "config/state.toml"


class StateManager:
    """
    状态管理器，负责读取、写入和操作状态数据。
    """

    def __init__(self, path=PATH):
        self.path = path
        self.state = self._read_state_from_file()

    def _read_state_from_file(self) -> dict:
        """从文件读取状态"""
        return toml.toml_read_state(self.path)

    def read_state(self) -> dict:
        """
        重新从文件读取状态
        Returns:
            dict: 状态数据
        """
        self.state = self._read_state_from_file()
        return self.state

    def write_state(self) -> None:
        """
        将当前状态写入文件
        """
        toml.toml_write_state(self.state, self.path)

    def get(self, key: str, default=None):
        """
        获取状态数据中的特定键的值
        Args:
            key (str): 键名
            default: 默认值，如果键不存在则返回
        Returns:
            值或默认值
        """
        return self.state.get(key, default)

    def set(self, key: str, value) -> None:
        """
        设置状态数据中的特定键的值，并写入文件
        Args:
            key (str): 键名
            value: 要设置的值
        """
        self.state[key] = value
        self.write_state()


# 实例化一个全局状态管理对象
state_manager = StateManager(PATH)
