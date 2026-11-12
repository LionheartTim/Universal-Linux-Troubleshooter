"""Dark Qt6 styling; all UI text increased by 2pt for readability."""

STYLESHEET = r"""
QMainWindow, QWidget#Root, QScrollArea#PageScroll, QWidget#ScrollContent {
    background: #0C1423;
    color: #EAF1FB;
}
QWidget { color: #EAF1FB; font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; font-size: 12pt; }
QLabel#BrandTitle { font-size: 24pt; font-weight: 750; color: #FFFFFF; }
QLabel#BrandSub { color: #9CACBF; font-size: 11pt; }
QLabel#SectionTitle { font-size: 20pt; font-weight: 700; color: #FFFFFF; }
QLabel#CardTitle { font-size: 15pt; font-weight: 700; color: #F3F7FF; }
QLabel#ResultTitle { font-size: 13pt; font-weight: 700; color: #F3F7FF; }
QLabel#CardBody { color: #B8C5D7; font-size: 12pt; }
QLabel#Muted { color: #97A8BF; }
QLabel#CountLabel { color: #86BBF3; font-size: 11pt; }
QLabel#Pill { background: #1A3047; border: 1px solid #275178; border-radius: 11px;
               padding: 4px 10px; color: #8FC9FF; font-weight: 700; font-size: 11pt; }
QLabel#QuietPill { background: #202838; border: 1px solid #3A4556; border-radius: 11px;
                    padding: 4px 10px; color: #C4CFDD; font-size: 11pt; }
QLabel#ResultBadge { background: #1C3048; border: 1px solid #34516D; border-radius: 7px;
    padding: 3px 9px; color: #B3C5DA; font-size: 11pt; font-weight: 700; }
QLabel#ResultBadge[resultState="ok"] { background: #18382E; border-color: #35765B; color: #9EE9BF; }
QLabel#ResultBadge[resultState="warning"] { background: #3B3120; border-color: #83672A; color: #FFE098; }
QLabel#ResultBadge[resultState="problem"] { background: #3D2528; border-color: #8C424A; color: #FFC5C9; }
QLabel#ResultBadge[resultState="unknown"] { background: #303246; border-color: #545F83; color: #CCCBFA; }
QLabel#ResultBadge[resultState="info"] { background: #1C3048; border-color: #34516D; color: #ADD5FF; }
QLabel#ResultBadge[resultState="not-run"] { background: #27303B; border-color: #4D5D70; color: #C1C9D1; }
QFrame#Card { background: #152136; border: 1px solid #293A54; border-radius: 15px; }
QFrame#AccentCard { background: #162A42; border: 1px solid #315B7D; border-radius: 15px; }
QFrame#Inset { background: #0D192B; border: 1px solid #2A3A51; border-radius: 10px; }
QFrame#ResultsPanel { background: #152136; border: 1px solid #2E405B; border-radius: 12px; }
QTabWidget::pane { border: 0px; background: #0C1423; }
QTabBar::tab { padding: 10px 18px; margin-right: 7px; color: #A9BED6;
                background: #17243A; border: 1px solid #293B54;
                border-top-left-radius: 8px; border-top-right-radius: 8px; }
QTabBar::tab:selected { background: #204468; color: white; border: 1px solid #417CA5; }
QTabBar::tab:hover:!selected { background: #1D314B; }
QTabWidget#ResultTabs::pane { border: 1px solid #2F415A; border-radius: 6px; background: #111D2E; }
QTabWidget#ResultTabs QTabBar::tab { padding: 7px 13px; margin-right: 3px; font-size: 11pt; }
QScrollArea#ResultsScroll, QScrollArea#ResultsScroll QWidget { background: #111D2E; }
QLineEdit { background: #0E1B2D; border: 1px solid #334961; border-radius: 9px;
            padding: 10px 12px; selection-background-color: #306B9E; }
QLineEdit:focus { border: 1px solid #64B5FF; }
QComboBox { background: #213752; border: 1px solid #3D5775; border-radius: 8px;
            padding: 7px 10px; min-height: 16px; color: #EAF1FB; }
QComboBox:hover { border: 1px solid #64B5FF; }
QComboBox::drop-down { width: 22px; border: none; }
QComboBox QAbstractItemView { background: #152136; color: #EAF1FB;
                               selection-background-color: #284C72;
                               selection-color: #FFFFFF; border: 1px solid #3D5775; }
QPushButton { background: #213752; border: 1px solid #3D5775; border-radius: 9px;
              padding: 8px 13px; font-weight: 600; }
QPushButton:hover:!disabled { background: #2A4868; border: 1px solid #5C87AB; }
QPushButton#Primary { background: #2475BF; border: 1px solid #3997EA; color: #FFFFFF; }
QPushButton#Primary:hover:!disabled { background: #3187D6; }
QPushButton#NewChatButton { background: #20364D; border: 1px solid #547493;
    border-radius: 9px; padding: 7px 14px; font-size: 11pt; }
QPushButton#NewChatButton:hover { background: #2A5274; }
QMessageBox { background: #152136; }
QMessageBox QLabel { color: #EDF4FC; }
QCheckBox { spacing: 9px; }
QPushButton:disabled { background: #1A2433; border: 1px solid #2C3949; color: #75879B; }
QListWidget { background: #111D2E; border: 1px solid #2B3D54; border-radius: 10px;
              padding: 5px; outline: 0px; }
QListWidget::item { padding: 10px 9px; border-radius: 7px; margin: 2px; }
QListWidget::item:selected { background: #235078; color: #FFFFFF; }
QListWidget::item:hover:!selected { background: #21334A; }
QTreeWidget { background: #111D2E; alternate-background-color: #162338;
               border: 1px solid #2B3D54; border-radius: 10px; outline: 0px; }
QTreeWidget::item { padding: 8px 5px; }
QTreeWidget::item:selected { background: #284C72; color: white; }
QHeaderView::section { background: #1B2A40; color: #C1D2E6; padding: 8px 6px;
                       border: none; border-bottom: 1px solid #3A4F69; font-weight: 700; }
QScrollBar:vertical { background: #102033; width: 11px; }
QScrollBar::handle:vertical { background: #355471; min-height: 25px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QToolTip { background: #26354B; border: 1px solid #5483AA; color: #F5F9FF; }
QPlainTextEdit#EvidenceText { background: #0C1727; color: #B6CADF; border: 1px solid #2B3D54;
    border-radius: 6px; font-family: monospace; font-size: 11pt; }
QTextEdit { background: #101C2E; border: 1px solid #2D3F58; border-radius: 10px; }
QScrollArea#ChatConversation, QWidget#ChatConversationBody {
    background: #0D1726; border: none;
}
QWidget#ChatThinkingRow { background: transparent; border: none; }
QLabel#ChatThinkingLabel { color: #B8CFE8; font-style: italic; font-size: 12pt; }
QFrame#ChatBubbleAssistant { background: #17283C; border: 1px solid #2E4863; border-radius: 15px; }
QFrame#ChatBubbleUser { background: #20466A; border: 1px solid #3F709A; border-radius: 15px; }
QLabel#ChatSpeaker { font-weight: 750; color: #B8DDFC; font-size: 11pt; }
QTextBrowser#ChatMessage { background: transparent; border: none; color: #EDF4FC;
                          font-size: 12pt; selection-background-color: #386D9D; }
QPushButton#ChatCopy { background: transparent; border: none; color: #9DBAD5; font-size: 10pt;
                       padding: 2px 6px; }
QFrame#ChatComposer { background: #13283C; border: 1px solid #46647C; border-radius: 13px; }
QPlainTextEdit#ChatInput { background: transparent; border: none; color: #F4F8FF;
                          padding: 6px; font-size: 12pt; }
QWidget#AppFooter { background: #101D2E; border-top: 1px solid #2B3D54; }
QLabel#FooterCredit { color: #ACBBD0; font-size: 11pt; }
QLabel#FooterCredit a { color: #7BBBF6; text-decoration: none; }
QLabel#FooterPreview { color: #7891AC; font-size: 10pt; }
QLabel#ProgressLabel { color: #9FC5EC; font-size: 11pt; }
"""

# v113: clearly separated, explicit repair approval (no auto-execution).
STYLESHEET += r"""
QFrame#RepairOfferCard { background: #172E40; border: 1px solid #497B9E; border-radius: 11px; }
QLabel#RepairOfferTitle { font-size: 13pt; font-weight: 750; color: #FFFFFF; }
QFrame#RepairOfferCard QLabel#Muted { color: #B9CDE2; font-style: italic; }
"""
