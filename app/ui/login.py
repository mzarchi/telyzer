from __future__ import annotations

import re
from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget, QStackedWidget,
)

from app.core.telegram import TelegramLoginWorker
from app.core.session import get_last_session_phone

_C = {
    "bg":     "#17212B", "card":   "#1E2C3A", "bar":    "#151E27",
    "blue":   "#2AABEE", "blue_h": "#1E96D6", "blue_d": "#1880BB",
    "white":  "#FFFFFF", "gray":   "#8B9DB0", "border": "#2B3E50",
    "input":  "#253340", "red":    "#E74C3C",
}

COUNTRIES: list[tuple[str, str]] = [
    ("🇮🇷 Iran",           "+98"),  ("🇺🇸 United States",  "+1"),
    ("🇬🇧 United Kingdom", "+44"),  ("🇩🇪 Germany",        "+49"),
    ("🇫🇷 France",         "+33"),  ("🇹🇷 Turkey",         "+90"),
    ("🇦🇪 UAE",            "+971"), ("🇷🇺 Russia",         "+7"),
    ("🇯🇵 Japan",          "+81"),  ("🇨🇳 China",          "+86"),
    ("🇮🇳 India",          "+91"),  ("🇧🇷 Brazil",         "+55"),
    ("🇨🇦 Canada",         "+1"),   ("🇦🇺 Australia",      "+61"),
    ("🇮🇹 Italy",          "+39"),  ("🇪🇸 Spain",          "+34"),
    ("🇳🇱 Netherlands",    "+31"),  ("🇸🇦 Saudi Arabia",   "+966"),
    ("🇵🇰 Pakistan",       "+92"),  ("🇧🇩 Bangladesh",     "+880"),
    ("🇸🇪 Sweden",         "+46"),  ("🇳🇴 Norway",         "+47"),
    ("🇩🇰 Denmark",        "+45"),  ("🇨🇭 Switzerland",    "+41"),
    ("🇵🇱 Poland",         "+48"),  ("🇺🇦 Ukraine",        "+380"),
]

_PHONE_RE = re.compile(r"^\d{7,15}$")

STYLESHEET = f"""
* {{ font-family: 'Segoe UI', Arial, sans-serif; }}

QWidget#TitleBar {{
    background-color: {_C['bar']};
    border-bottom: 1px solid {_C['border']};
}}
QLabel#AppName {{
    color: {_C['gray']}; font-size: 12px;
    font-weight: 600; letter-spacing: 1px;
}}
QPushButton#BtnClose, QPushButton#BtnMin {{
    background: transparent; border: none;
    color: {_C['gray']}; font-size: 15px;
    min-width: 28px; min-height: 28px; border-radius: 6px;
}}
QPushButton#BtnClose:hover {{ background: {_C['red']}; color: white; }}
QPushButton#BtnMin:hover   {{ background: {_C['border']}; color: white; }}

QLabel#Logo     {{ color: {_C['blue']}; font-size: 58px; }}
QLabel#Title    {{ color: {_C['white']}; font-size: 22px; font-weight: bold; }}
QLabel#Subtitle {{ color: {_C['gray']}; font-size: 13px; line-height: 1.5; }}
QLabel#FieldLbl {{
    color: {_C['gray']}; font-size: 10px;
    font-weight: 700; letter-spacing: .8px;
}}
QLabel#ErrLbl   {{ color: {_C['red']}; font-size: 11px; }}
QLabel#PrivacyLbl {{
    color: {_C['gray']}; font-size: 11px;
}}

QLineEdit {{
    background: {_C['input']}; color: {_C['white']};
    border: 1.5px solid {_C['border']}; border-radius: 10px;
    padding: 11px 14px; font-size: 15px;
    selection-background-color: {_C['blue']};
}}
QLineEdit:focus {{ border-color: {_C['blue']}; }}

QPushButton#CountryBtn {{
    background: {_C['input']}; color: {_C['white']};
    border: 1.5px solid {_C['border']}; border-radius: 10px;
    padding: 11px 8px; font-size: 13px; font-weight: bold;
    min-width: 84px; max-width: 84px;
}}
QPushButton#CountryBtn:hover   {{ border-color: {_C['blue']}; background: #2A3F52; }}
QPushButton#CountryBtn:pressed {{ background: {_C['blue']}; color: white; border-color: {_C['blue']}; }}

QPushButton#SendBtn {{
    background: {_C['blue']}; color: white; border: none;
    border-radius: 10px; padding: 13px;
    font-size: 15px; font-weight: bold;
}}
QPushButton#SendBtn:hover   {{ background: {_C['blue_h']}; }}
QPushButton#SendBtn:pressed {{ background: {_C['blue_d']}; }}

QCheckBox {{
    color: {_C['gray']}; font-size: 12px; spacing: 8px;
}}
QCheckBox::indicator {{
    width: 17px; height: 17px; border-radius: 5px;
    border: 1.5px solid {_C['border']}; background: {_C['input']};
}}
QCheckBox::indicator:hover   {{ border-color: {_C['blue']}; }}
QCheckBox::indicator:checked {{
    background: {_C['blue']}; border-color: {_C['blue']};
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMiAxMiI+PHBhdGggZD0iTTIgNmwzIDMgNS01IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==");
}}

QListWidget {{
    background: {_C['input']}; color: {_C['white']};
    border: 1px solid {_C['border']}; border-radius: 8px;
    font-size: 13px; outline: none;
}}
QListWidget::item        {{ padding: 9px 14px; border-bottom: 1px solid #1E2C3A; }}
QListWidget::item:selected {{ background: {_C['blue']}; color: white; }}
QListWidget::item:hover    {{ background: {_C['border']}; }}
QScrollBar:vertical {{
    background: {_C['input']}; width: 5px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {_C['border']}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


class CountryDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(290, 400)
        self.selected: Optional[tuple[str, str]] = None
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setStyleSheet(
            f"QWidget {{ background:{_C['card']}; border:1px solid {_C['border']};"
            f" border-radius:12px; }}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        hdr = QLabel("Select Country")
        hdr.setStyleSheet(
            f"color:{_C['white']}; font-size:15px; font-weight:bold; border:none;")
        lay.addWidget(hdr)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search country or code…")
        self._search.textChanged.connect(self._filter)
        lay.addWidget(self._search)

        self._lst = QListWidget()
        self._lst.itemClicked.connect(self._pick)
        lay.addWidget(self._lst)

        root.addWidget(card)
        self._fill(COUNTRIES)

    def _fill(self, items: list[tuple[str, str]]) -> None:
        self._lst.clear()
        for name, code in items:
            it = QListWidgetItem(f"{name}   {code}")
            it.setData(Qt.ItemDataRole.UserRole, (name.split()[0], code))
            self._lst.addItem(it)

    def _filter(self, txt: str) -> None:
        q = txt.lower()
        self._fill([(n, c) for n, c in COUNTRIES if q in n.lower() or q in c])

    def _pick(self, item: QListWidgetItem) -> None:
        self.selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()


class TitleBar(QWidget):
    def __init__(self, win: QWidget) -> None:
        super().__init__(win)
        self.setObjectName("TitleBar")
        self.setFixedHeight(36)
        self._drag: Optional[QPoint] = None

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(6)

        icon = QLabel("📊")
        icon.setStyleSheet(f"color:{_C['blue']}; font-size:13px; border:none;")
        lay.addWidget(icon)

        name = QLabel("Telyzer")
        name.setObjectName("AppName")
        lay.addWidget(name)

        lay.addStretch()

        for obj, text, slot in (
            ("BtnMin",   "─", win.showMinimized),
            ("BtnClose", "✕", win.close),
        ):
            btn = QPushButton(text)
            btn.setObjectName(obj)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            lay.addWidget(btn)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None


class LoginWindow(QWidget):
    SHADOW_MARGIN = 3

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 580)
        self._drag: Optional[QPoint] = None

        self._flag = "🇮🇷"
        self._code = "+98"
        self.worker: Optional[TelegramLoginWorker] = None
        self._session_checker: Optional[TelegramLoginWorker] = None

        self._build()
        self._check_existing_session()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        m = self.SHADOW_MARGIN
        outer.setContentsMargins(m, m, m, m)
        outer.setSpacing(0)

        card = QWidget()
        card.setObjectName("MainCard")
        card.setStyleSheet(
            f"#MainCard {{ background: {_C['bg']}; border-radius: 14px; border: 1px solid rgba(255,255,255,14); }}"
        )

        vlay = QVBoxLayout(card)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)

        vlay.addWidget(TitleBar(self))

        self.stack = QStackedWidget()

        self.page_login = self._make_body()
        self.page_empty = QWidget()
        self.page_empty.setStyleSheet(
            f"background: {_C['bg']}; border-bottom-left-radius:14px; border-bottom-right-radius:14px;")

        self.stack.addWidget(self.page_empty)
        self.stack.addWidget(self.page_login)

        self.stack.setCurrentWidget(self.page_empty)

        vlay.addWidget(self.stack)
        outer.addWidget(card)

    def _make_body(self) -> QWidget:
        body = QWidget()
        self._layout = QVBoxLayout(body)
        self._layout.setContentsMargins(44, 20, 44, 20)
        self._layout.setSpacing(0)

        logo = QLabel("📊")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(logo)
        self._layout.addSpacing(6)

        title = QLabel("Telyzer")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(title)
        self._layout.addSpacing(4)

        self._sub = QLabel(
            "Please confirm your country code\nand enter your phone number.")
        self._sub.setObjectName("Subtitle")
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setWordWrap(True)
        self._layout.addWidget(self._sub)
        self._layout.addSpacing(16)

        self._field_lbl = QLabel("YOUR NUMBER")
        self._field_lbl.setObjectName("FieldLbl")
        self._layout.addWidget(self._field_lbl)
        self._layout.addSpacing(5)

        self._row_layout_widget = QWidget()
        row = QHBoxLayout(self._row_layout_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._country_btn = QPushButton(f"{self._flag}  {self._code}")
        self._country_btn.setObjectName("CountryBtn")
        self._country_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._country_btn.clicked.connect(self._pick_country)
        row.addWidget(self._country_btn)

        self._phone = QLineEdit()
        self._phone.setPlaceholderText("912 345 6789")
        self._phone.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._phone.textChanged.connect(self._on_input_change)
        row.addWidget(self._phone)

        self._layout.addWidget(self._row_layout_widget)

        self._code_input = QLineEdit()
        self._code_input.setPlaceholderText("Enter verification code")
        self._code_input.setVisible(False)
        self._layout.addWidget(self._code_input)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Enter 2FA Password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setVisible(False)
        self._layout.addWidget(self._password_input)
        self._layout.addSpacing(8)

        self._remember = QCheckBox("Remember me")
        self._remember.setChecked(True)
        self._remember.setCursor(Qt.CursorShape.PointingHandCursor)
        self._layout.addWidget(self._remember)
        self._layout.addSpacing(6)

        self._err = QLabel(" ")
        self._err.setObjectName("ErrLbl")
        self._err.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._err.setFixedHeight(16)
        self._layout.addWidget(self._err)
        self._layout.addSpacing(10)

        self._send_btn = QPushButton("Send Code")
        self._send_btn.setObjectName("SendBtn")
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.clicked.connect(self._on_send)
        self._layout.addWidget(self._send_btn)
        self._layout.addSpacing(16)

        privacy = QLabel(
            '<div style="line-height: 1.5; text-align: center;">'
            'By signing in, you agree to our<br>'
            '<a href="#" style="color:#2AABEE; text-decoration:none;">Privacy Policy</a>'
            ' and '
            '<a href="#" style="color:#2AABEE; text-decoration:none;">Terms of Service</a>.'
            '</div>'
        )
        privacy.setObjectName("PrivacyLbl")
        privacy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        privacy.setTextFormat(Qt.TextFormat.RichText)
        privacy.setOpenExternalLinks(False)
        privacy.setWordWrap(True)
        self._layout.addWidget(privacy)
        return body

    # ----------------------------------------------------
    # Auto-Login Logic
    # ----------------------------------------------------

    def _check_existing_session(self) -> None:
        phone = get_last_session_phone()

        if not phone:
            self.stack.setCurrentWidget(self.page_login)
            return

        self._session_checker = TelegramLoginWorker(phone, remember=True)
        self._session_checker.session_checked.connect(
            self._on_session_check_result)
        self._session_checker.start()
        self._session_checker.check_active_session()

    def _on_session_check_result(self, is_authorized: bool) -> None:
        if is_authorized:
            self.stack.setCurrentWidget(self.page_empty)
        else:
            self.stack.setCurrentWidget(self.page_login)

    # ----------------------------------------------------

    def _on_input_change(self, text: str) -> None:
        if text:
            self._err.setText(" ")

    def _pick_country(self) -> None:
        dlg = CountryDialog(self)
        dlg.setStyleSheet(STYLESHEET)
        POPUP_Y_OFFSET = -40
        pos = self._country_btn.mapToGlobal(QPoint(0, POPUP_Y_OFFSET))
        dlg.move(pos)
        if dlg.exec() and dlg.selected:
            self._flag, self._code = dlg.selected
            self._country_btn.setText(f"{self._flag}  {self._code}")

    def _on_send(self):
        raw = self._phone.text().strip()
        phone = "".join(ch for ch in raw if ch.isdigit())

        if phone.startswith("0"):
            phone = phone[1:]

        if not _PHONE_RE.match(phone):
            self._err.setText("⚠ Enter a valid number")
            return

        self._err.setText("Sending code...")
        self._send_btn.setEnabled(False)

        full_number = f"{self._code}{phone}"
        remember = self._remember.isChecked()

        self.worker = TelegramLoginWorker(full_number, remember)
        self.worker.code_sent.connect(self._on_code_sent)
        self.worker.need_password.connect(self._on_need_password)
        self.worker.login_success.connect(self._on_login_success)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()
        self.worker.send_code()

    def _on_code_sent(self):
        self._send_btn.setEnabled(True)
        self._err.setText("Verification code sent.")

        self._row_layout_widget.setVisible(False)
        self._field_lbl.setText("VERIFICATION CODE")
        self._code_input.setVisible(True)
        self._code_input.setFocus()

        self._send_btn.setText("Confirm Code")
        self._send_btn.clicked.disconnect()
        self._send_btn.clicked.connect(self._submit_code)

    def _submit_code(self):
        code = self._code_input.text().strip()
        if not code:
            self._err.setText("⚠ Enter the code you received")
            return
        self._err.setText("Checking code...")
        if self.worker:
            self.worker.submit_code(code)

    def _on_need_password(self):
        self._err.setText("Two-Step Verification active.")

        self._code_input.setVisible(False)
        self._field_lbl.setText("2FA PASSWORD")
        self._password_input.setVisible(True)
        self._password_input.setFocus()

        self._send_btn.setText("Verify Password")
        self._send_btn.clicked.disconnect()
        self._send_btn.clicked.connect(self._submit_password)

    def _submit_password(self):
        pwd = self._password_input.text().strip()
        if not pwd:
            self._err.setText("⚠ Enter your 2FA password")
            return
        self._err.setText("Checking password...")
        if self.worker:
            self.worker.submit_password(pwd)

    def _on_login_success(self, status):
        self.stack.setCurrentWidget(self.page_empty)

    def _on_error(self, err_msg):
        self._send_btn.setEnabled(True)
        self._err.setText(f"⚠ {err_msg}")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        if self._session_checker:
            self._session_checker.stop()
            self._session_checker.wait()
        event.accept()

    def paintEvent(self, _) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = self.SHADOW_MARGIN
        for i in range(m, 0, -1):
            alpha = int(28 * (i / m) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            p.drawRoundedRect(
                self.rect().adjusted(m - i, m - i, i - m, i - m),
                15, 15,
            )
