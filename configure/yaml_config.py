import os
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

# 带注释的默认模板
default_template = CommentedMap({
    'default': CommentedMap({
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root'
    }),
    'dev': CommentedMap({
        '<<': {'*default': None},  # 继承示例
        'database': 'dev_db'
    }),
    'prod': CommentedMap({
        '<<': {'*default': None},
        'host': 'prod-server',
        'database': 'prod_db'
    })
})

# 添加注释
default_template.yaml_set_comment_before_after_key('default', before="====== 默认数据库配置 ======")
default_template['default'].yaml_add_eol_comment("数据库主机", 'host')
default_template['default'].yaml_add_eol_comment("端口号", 'port')
default_template['default'].yaml_add_eol_comment("用户名", 'user')
default_template['default'].yaml_add_eol_comment("密码", 'password')


class YamlConfig:
    def __init__(self, filepath: str, default_template: dict = None):
        """
        :param filepath: YAML 配置文件路径
        :param default_template: 如果文件不存在，使用的默认配置（可带注释）
        """
        self.filepath = filepath
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # 保留引号
        self.yaml.indent(sequence=4, offset=2)  # 缩进设置
        self.data = None

        if os.path.exists(filepath):
            self.load()
        else:
            # 文件不存在时，写入默认模板
            if default_template:
                self.data = default_template
                self.save()
            else:
                self.data = {}

    def load(self):
        """加载 YAML 配置"""
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.data = self.yaml.load(f)

    def save(self):
        """保存 YAML 配置"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            self.yaml.dump(self.data, f)

    def get(self, key_path: str, default=None):
        """
        按路径取值，例如 "database.host"
        """
        keys = key_path.split(".")
        node = self.data
        for k in keys:
            if node is None or k not in node:
                return default
            node = node[k]
        return node

    def set(self, key_path: str, value):
        """
        按路径设值，例如 "database.port", 3306
        """
        keys = key_path.split(".")
        node = self.data
        for k in keys[:-1]:
            if k not in node:
                node[k] = {}
            node = node[k]
        node[keys[-1]] = value


if __name__ == '__main__':
    cfg = YamlConfig("config.yaml", default_template=default_template)

    print(cfg.get("dev.database"))  # dev_db
    print(cfg.get("prod.host"))  # prod-server

    cfg.set("prod.password", "new_pass123")
    cfg.save()
