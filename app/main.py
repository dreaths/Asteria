import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QCalendarWidget,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteria")

        calendar = QCalendarWidget()

        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Today's Reminders"))
        sidebar.addWidget(QPushButton("Add Event"))
        sidebar.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(calendar, stretch=3)
        main_layout.addLayout(sidebar, stretch=1)

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#B5483D"))
        calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor("#4A4258"))
        for day in [Qt.DayOfWeek.Monday, Qt.DayOfWeek.Tuesday, Qt.DayOfWeek.Wednesday,
                    Qt.DayOfWeek.Thursday, Qt.DayOfWeek.Friday]:
            calendar.setWeekdayTextFormat(day, weekday_format)
        
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
    QMainWindow {
        background-color: #F5F1FA;
    }
    QCalendarWidget {
        background-color: #F5F1FA;
        border: none;
    }
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5DCEF;
    }
    QCalendarWidget QToolButton {
        color: #4A4258;
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QCalendarWidget QToolButton:hover {
        background-color: #C9A8E0;
        color: #FFFFFF;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #F5F1FA;
        color: #4A4258;
        selection-background-color: #C9A8E0;
        selection-color: #FFFFFF;
        outline: none;
        gridline-color: #E5DCEF;
    }
    QCalendarWidget QAbstractItemView:disabled {
        color: #B7ABC6;
    }

                      
    QPushButton {
        background-color: #FFFFFF;
        color: #4A4258;
        border: 1px solid #F2A88A;
        border-radius: 6px;
        padding: 6px;
    }
    QPushButton:hover {
        background-color: #F2A88A;
        color: #FFFFFF;
    }
""")

    window = MainWindow()
    window.resize(900, 650)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()