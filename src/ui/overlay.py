import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

# Farbpalette passend zu den Nutzeranforderungen (Orange / Beige, soft)
COLOR_BEIGE = QColor("#F4EFE6") # Weiches Beige für den Hintergrund
COLOR_ORANGE = QColor("#E07A5F") # Weiches Orange (nicht zu knallig)

class AudioVisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 30)
        self.amplitudes = [0.05] * 10
        
    @pyqtSlot(list)
    def update_amplitudes(self, data):
        """Erwartet eine Liste von Float-Werten zwischen 0.0 und 1.0"""
        self.amplitudes = data
        self.update() # Löst paintEvent aus
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        bar_width = width / len(self.amplitudes)
        spacing = 4
        
        painter.setBrush(COLOR_ORANGE)
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i, amp in enumerate(self.amplitudes):
            amp = max(0.05, min(1.0, amp))
            bar_h = height * amp
            x = i * bar_width + spacing / 2
            y = (height - bar_h) / 2 # Vertikal zentrieren
            
            # Abgerundete Balken
            painter.drawRoundedRect(int(x), int(y), int(bar_width - spacing), int(bar_h), 2, 2)

class OverlayWindow(QWidget):
    # Thread-sicheres Signal für Audio-Updates
    audio_update_signal = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        
        # Rahmenlos, Immer im Vordergrund, wird oft nicht in der Taskleiste angezeigt (als Tool)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Wichtig: Transparenter Hintergrund der eigentlichen GUI-Box, 
        # damit wir abgerundete Ecken im paintEvent zeichnen können.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(15)
        
        # Logo Label ("L" in Times New Roman)
        self.logo_label = QLabel("L")
        font = QFont("Times New Roman", 28, QFont.Weight.Bold)
        self.logo_label.setFont(font)
        self.logo_label.setStyleSheet(f"color: {COLOR_ORANGE.name()};")
        self.layout.addWidget(self.logo_label)
        
        # Audio Visualizer
        self.visualizer = AudioVisualizerWidget()
        self.layout.addWidget(self.visualizer)
        
        # Signal verbinden
        self.audio_update_signal.connect(self.visualizer.update_amplitudes)
        
        # Geometrie verzögert setzen, damit die Breite nach dem Layouten bekannt ist
        QTimer.singleShot(0, self.setup_geometry)
        
    def setup_geometry(self):
        self.resize(200, 60)
        self.center_at_bottom()

    def center_at_bottom(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 60  # Ein wenig Abstand zur Taskleiste (unten)
        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(COLOR_BEIGE)
        
        # Feiner Rand
        pen = QPen(QColor("#E5E0D8"))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Hintergrund box
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 15, 15)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec())
