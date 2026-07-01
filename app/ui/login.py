from __future__ import annotations

import re
import sys
from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QBrush, QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════

# Central color palette.
_C = {
    "bg":     "#17212B", "card":   "#1E2C3A", "bar":    "#151E27",
    "blue":   "#2AABEE", "blue_h": "#1E96D6", "blue_d": "#1880BB",
    "white":  "#FFFFFF", "gray":   "#8B9DB0", "border": "#2B3E50",
    "input":  "#253340", "red":    "#E74C3C",
}

# (flag + country name, dial code)
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

# Digits only, 7–15 chars.
_PHONE_RE = re.compile(r"^\d{7,15}$")

# Widget styling (QSS)
STYLESHEET = f"""
* {{ font-family: 'Segoe UI', Arial, sans-serif; }}

/* ── titlebar ── */
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

/* ── content ── */
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
    line-height: 1.6;
}}

/* ── inputs ── */
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

/* ── Send Code button ── */
QPushButton#SendBtn {{
    background: {_C['blue']}; color: white; border: none;
    border-radius: 10px; padding: 13px;
    font-size: 15px; font-weight: bold;
}}
QPushButton#SendBtn:hover   {{ background: {_C['blue_h']}; }}
QPushButton#SendBtn:pressed {{ background: {_C['blue_d']}; }}

/* ── Remember Me ── */
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

/* ── country list ── */
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
    """Country picker with search"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        # Auto-close popup
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(290, 400)
        self.selected: Optional[tuple[str, str]] = None  # (flag, code)
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
            f"color:{_C['white']}; font-size:15px; font-weight:bold; border:none;"
        )
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
        """Refresh list"""
        self._lst.clear()
        for name, code in items:
            it = QListWidgetItem(f"{name}   {code}")
            it.setData(Qt.ItemDataRole.UserRole, (name.split()[0], code))
            self._lst.addItem(it)

    def _filter(self, txt: str) -> None:
        """Filter as user types"""
        q = txt.lower()
        self._fill([(n, c) for n, c in COUNTRIES if q in n.lower() or q in c])

    def _pick(self, item: QListWidgetItem) -> None:
        self.selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()


class TitleBar(QWidget):
    """Custom draggable titlebar"""

    def __init__(self, win: QWidget) -> None:
        super().__init__(win)
        self.setObjectName("TitleBar")
        self.setFixedHeight(36)
        self._drag: Optional[QPoint] = None

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(6)

        icon = QLabel("✈")
        icon.setStyleSheet(f"color:{_C['blue']}; font-size:13px; border:none;")
        lay.addWidget(icon)

        name = QLabel("TELYZER")
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

    # ── window drag handling ──
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = (
                e.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None


class LoginWindow(QWidget):
    """Frameless draggable login screen"""
    
    SHADOW_MARGIN = 3

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 570)
        self._drag: Optional[QPoint] = None

        self._flag = "🇮🇷"
        self._code = "+98"

        self._build()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    # ── UI setup ──

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        m = self.SHADOW_MARGIN
        outer.setContentsMargins(m, m, m, m)
        outer.setSpacing(0)

        card = QWidget()
        card.setObjectName("MainCard")
        card.setStyleSheet(
            f"""
            #MainCard {{
            background: {_C['bg']};
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,14);
            }}
            """
        )
        vlay = QVBoxLayout(card)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)
        vlay.addWidget(TitleBar(self))
        vlay.addWidget(self._make_body())

        outer.addWidget(card)

    def _make_body(self) -> QWidget:
        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setContentsMargins(44, 28, 44, 28)
        lay.setSpacing(0)

        # ── Header ──
        logo = QLabel("✈")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo)
        lay.addSpacing(8)

        title = QLabel("Telyzer")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        lay.addSpacing(6)

        sub = QLabel("Please confirm your country code\nand enter your phone number.")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addSpacing(24)

        lbl = QLabel("YOUR NUMBER")
        lbl.setObjectName("FieldLbl")
        lay.addWidget(lbl)
        lay.addSpacing(5)

        row = QHBoxLayout()
        row.setSpacing(8)

        self._country_btn = QPushButton(f"{self._flag}  {self._code}")
        self._country_btn.setObjectName("CountryBtn")
        self._country_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._country_btn.clicked.connect(self._pick_country)
        row.addWidget(self._country_btn)

        self._phone = QLineEdit()
        self._phone.setPlaceholderText("912 345 6789")
        self._phone.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._phone.textChanged.connect(self._on_input_change)
        row.addWidget(self._phone)

        lay.addLayout(row)
        lay.addSpacing(6)

        # ── Options ──
        self._remember = QCheckBox("Remember me")
        self._remember.setCursor(Qt.CursorShape.PointingHandCursor)
        lay.addWidget(self._remember)
        lay.addSpacing(6)

        # ── Error label (prevent layout jump) ──
        self._err = QLabel(" ")
        self._err.setObjectName("ErrLbl")
        self._err.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._err.setFixedHeight(16)
        lay.addWidget(self._err)
        lay.addSpacing(12)

        # ── Send button ──
        self._send_btn = QPushButton("Send Code")
        self._send_btn.setObjectName("SendBtn")
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.clicked.connect(self._on_send)
        lay.addWidget(self._send_btn)
        lay.addSpacing(20)

        # ── privacy ──
        privacy = QLabel(
            'By signing in, you agree to our\n'
            '<a href="#" style="color:#2AABEE; text-decoration:none;">Privacy Policy</a>'
            ' and '
            '<a href="#" style="color:#2AABEE; text-decoration:none;">Terms of Service</a>.'
        )
        privacy.setObjectName("PrivacyLbl")
        privacy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        privacy.setTextFormat(Qt.TextFormat.RichText)
        privacy.setOpenExternalLinks(False)
        lay.addWidget(privacy)

        return body

    # ── logic ──

    def _on_input_change(self, text: str) -> None:
        if text:
            self._err.setText(" ")

    def _pick_country(self) -> None:
        dlg = CountryDialog(self)
        dlg.setStyleSheet(STYLESHEET)

        # Popup Y offset (negative = up)
        POPUP_Y_OFFSET = -40

        pos = self._country_btn.mapToGlobal(QPoint(0, POPUP_Y_OFFSET))
        dlg.move(pos)
        if dlg.exec() and dlg.selected:
            self._flag, self._code = dlg.selected
            self._country_btn.setText(f"{self._flag}  {self._code}")

    def _on_send(self):
        """UI-only send handler"""
        raw = self._phone.text().strip()
        phone = raw.lstrip("0")

        if not _PHONE_RE.match(phone):
            self._err.setText("⚠ Enter a valid number")
            return

        self._err.setText(" ")
        full = f"{self._code}{phone}"
        print(f"[Telyzer] Number entered → {full}  |  Remember me: {self._remember.isChecked()}")

    # ── window shadow ──

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

# ════════════════════════════════════════════════════════════════

def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    win = LoginWindow()
    win.setStyleSheet(STYLESHEET)

    geo = app.primaryScreen().availableGeometry()
    win.move(
        (geo.width()  - win.width())  // 2,
        (geo.height() - win.height()) // 2,
    )
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
