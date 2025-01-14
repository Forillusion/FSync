from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel
from qfluentwidgets import ScrollArea, ExpandLayout, SettingCardGroup, OptionsSettingCard, CustomColorSettingCard, \
    Theme, SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import setThemeColor, isDarkTheme, setTheme
from PySide6.QtCore import Qt, Signal
from UI.config import cfg

class SettingWindow(ScrollArea):
    # themeChangeMsg = pyqtSignal(str)
    themeChangeMsg = Signal(str)


    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingWindow")

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel("设置", self)


        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.personalGroup
        )

        self.themeColorCard=CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            "主题色",
            "调整你的应用主题颜色",
            self.personalGroup
        )
        self.resetThemeColorCard()

        self.silentStartCard = SwitchSettingCard(
            icon=FIF.TRANSPARENT,
            title="静默启动",
            content="",
            configItem=cfg.silentStart,
            parent=self.personalGroup
        )

        # setThemeColor("#BDDD9A")
        # self.themeColorCard.__initWidget()

        # self.languageCard = ComboBoxSettingCard(
        #     cfg.language,
        #     FIF.LANGUAGE,
        #     self.tr('Language'),
        #     self.tr('Set your preferred language for UI'),
        #     texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
        #     parent=self.personalGroup
        # )


        self.__initWidget()

    def resetThemeColorCard(self):

        self.themeColorCard.defaultColor = QColor("#BDDD9A")

        if self.themeColorCard.defaultColor != self.themeColorCard.customColor:
            self.themeColorCard.customRadioButton.setChecked(True)
            self.themeColorCard.chooseColorButton.setEnabled(True)
        else:
            self.themeColorCard.defaultRadioButton.setChecked(True)
            self.themeColorCard.chooseColorButton.setEnabled(False)
        self.themeColorCard.choiceLabel.setText(self.themeColorCard.buttonGroup.checkedButton().text())


    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)    # 设置水平滚动条的显示方式
        self.setViewportMargins(0, 60, 0, 20)   # 设置滚动区域的边距
        self.setWidget(self.scrollWidget)  # 设置滚动区域的窗口部件
        self.setWidgetResizable(True)   # 设置滚动区域的窗口部件是否可以调整大小

        # # 改为透明背景并移除边框
        # self.setStyleSheet("QScrollArea{background: transparent; border: none}")
        # # 必须给内部的视图也加上透明背景样式
        # self.scrollWidget.setStyleSheet("QWidget{background: transparent}")

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 25   )

        # # add cards to group
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.silentStartCard)


        # add setting card group to layout
        self.expandLayout.setSpacing(28) # 设置组件之间的间距
        self.expandLayout.setContentsMargins(60, 10, 60, 0) # 设置组件与窗口边缘的距离
        self.expandLayout.addWidget(self.personalGroup)

        # self.grid = QGridLayout()
        # self.grid.setSpacing(5)
        # self.setLayout(self.grid) # 将grid布局添加到窗口中
        #
        # self.grid.addWidget(self.personalGroup, 3, 0)
        # self.grid.addWidget(self.settingLabel, 1, 0)

    def __setQss(self):
        self.settingLabel.setObjectName('settingLabel')
        theme = 'dark' if isDarkTheme() else 'light'
        self.themeChangeMsg.emit(theme)

        with open(f'UI/resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


    def __connectSignalToSlot(self):
        self.themeColorCard.colorChanged.connect(setThemeColor)
        cfg.themeChanged.connect(self.__onThemeChanged)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)
        # change the theme of setting interface
        self.__setQss()

