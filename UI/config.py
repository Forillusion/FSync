from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import QConfig, qconfig,RangeConfigItem,RangeValidator,OptionsConfigItem,OptionsValidator,ConfigSerializer


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)  # QLocale.Chinese:中文 QLocale.China:中国
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong) # QLocale.Chinese:中文 QLocale.HongKong:香港
    ENGLISH = QLocale(QLocale.English) # QLocale.English:英文
    AUTO = QLocale() # Auto detect


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO

class Config(QConfig):
    # themeMode = Enum('ThemeMode', 'LIGHT DARK SYSTEM')
    language = OptionsConfigItem("MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

cfg = Config()
qconfig.load('UI\config.json', cfg)