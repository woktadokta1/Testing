import datetime
import logging
from typing import Set

logger = logging.getLogger(__name__)

try:
    from aqt.qt import *
    from aqt.utils import showInfo
    from heatmap_widget import HeatmapWidget
    from utils import get_review_data, load_selections, save_selections
except Exception as e:
    logger.error(f"Import error: {e}", exc_info=True)
    raise

class HeatmapWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setWindowTitle("Review Heatmap with Date Selector")
            self.setGeometry(100, 100, 1400, 600)
            self.setWindowModality(Qt.ApplicationModal)
            
            self.time_range = "36months"
            self.review_data = self.fetch_review_data()
            self.selected_dates: Set[str] = set(load_selections())
            
            self.init_ui()
            self.load_initial_selection()
            logger.info("HeatmapWindow initialized")
        except Exception as e:
            logger.error(f"Init error: {e}", exc_info=True)
            showInfo(f"Error: {str(e)}")
            raise
    
    def fetch_review_data(self):
        try:
            months = {
                "1month": 1,
                "3months": 3,
                "6months": 6,
                "12months": 12,
                "24months": 24,
                "36months": 36,
            }.get(self.time_range, 36)
            data = get_review_data(months)
            logger.info(f"Fetched data for {self.time_range}")
            return data
        except Exception as e:
            logger.error(f"Fetch error: {e}", exc_info=True)
            return {}
    
    def init_ui(self):
        try:
            main_layout = QHBoxLayout(self)
            sidebar = self.create_sidebar()
            main_layout.addWidget(sidebar, 0)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            self.heatmap_widget = HeatmapWidget(self.review_data, self)
            self.heatmap_widget.set_selected_dates(self.selected_dates)
            self.heatmap_widget.selection_changed.connect(self.on_selection_changed)
            
            scroll_area.setWidget(self.heatmap_widget)
            main_layout.addWidget(scroll_area, 1)
            self.setLayout(main_layout)
        except Exception as e:
            logger.error(f"UI init error: {e}", exc_info=True)
            raise
    
    def create_sidebar(self):
        try:
            sidebar = QWidget()
            layout = QVBoxLayout(sidebar)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            title = QLabel("Review Heatmap")
            title.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(title)
            
            layout.addWidget(QLabel("Time Range:"))
            time_range_group = QGroupBox()
            range_layout = QVBoxLayout(time_range_group)
            
            ranges = [
                ("1 Month", "1month"),
                ("3 Months", "3months"),
                ("6 Months", "6months"),
                ("12 Months", "12months"),
                ("24 Months", "24months"),
                ("36 Months (3 Years)", "36months"),
            ]
            
            self.time_range_buttons = {}
            for label, value in ranges:
                btn = QRadioButton(label)
                btn.setChecked(value == self.time_range)
                btn.toggled.connect(lambda checked, v=value: self.on_time_range_changed(v, checked))
                self.time_range_buttons[value] = btn
                range_layout.addWidget(btn)
            
            layout.addWidget(time_range_group)
            
            layout.addWidget(QLabel("Statistics:"))
            stats_group = QGroupBox()
            stats_layout = QVBoxLayout(stats_group)
            
            self.selected_count_label = QLabel("Selected: 0 dates")
            self.selected_count_label.setStyleSheet("font-weight: bold; color: #0040B0;")
            stats_layout.addWidget(self.selected_count_label)
            
            try:
                days_with_reviews = sum(1 for v in self.review_data.values() if v > 0)
                total_reviews = sum(self.review_data.values())
                stats_layout.addWidget(QLabel(f"Days with reviews: {days_with_reviews}"))
                stats_layout.addWidget(QLabel(f"Total reviews: {total_reviews}"))
            except Exception as e:
                logger.warning(f"Stats error: {e}")
                stats_layout.addWidget(QLabel("Days with reviews: N/A"))
                stats_layout.addWidget(QLabel("Total reviews: N/A"))
            
            layout.addWidget(stats_group)
            
            layout.addWidget(QLabel("Actions:"))
            
            self.btn_save = QPushButton("Save Selection")
            self.btn_save.clicked.connect(self.on_save_clicked)
            self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
            layout.addWidget(self.btn_save)
            
            self.btn_export = QPushButton("Export Selected Dates")
            self.btn_export.clicked.connect(self.on_export_clicked)
            self.btn_export.setStyleSheet("background-color: #0040B0; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
            layout.addWidget(self.btn_export)
            
            self.btn_clear = QPushButton("Clear Selection")
            self.btn_clear.clicked.connect(self.on_clear_clicked)
            self.btn_clear.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
            layout.addWidget(self.btn_clear)
            
            layout.addSpacing(20)
            help_text = QLabel(
                "<b>How to use:</b><br>"
                "• <b>Left-click</b> dates to select<br>"
                "• <b>Black box</b> = selected<br>"
                "• Click <b>Save</b> to persist<br>"
                "• <b>Right-click</b> for menu"
            )
            help_text.setWordWrap(True)
            help_text.setStyleSheet("font-size: 9px; padding: 8px; background-color: #f5f5f5; border-radius: 4px; border: 1px solid #ddd;")
            layout.addWidget(help_text)
            
            layout.addStretch()
            sidebar.setMaximumWidth(280)
            sidebar.setMinimumWidth(200)
            return sidebar
        except Exception as e:
            logger.error(f"Sidebar error: {e}", exc_info=True)
            raise
    
    def load_initial_selection(self):
        try:
            self.update_selection_count()
            if self.heatmap_widget:
                self.heatmap_widget.set_selected_dates(self.selected_dates)
        except Exception as e:
            logger.error(f"Load selection error: {e}", exc_info=True)
    
    def on_selection_changed(self):
        try:
            self.selected_dates = self.heatmap_widget.get_selected_dates()
            self.update_selection_count()
        except Exception as e:
            logger.error(f"Selection change error: {e}", exc_info=True)
    
    def update_selection_count(self):
        try:
            count = len(self.selected_dates)
            plural = 's' if count != 1 else ''
            self.selected_count_label.setText(f"Selected: {count} date{plural}")
        except Exception as e:
            logger.warning(f"Count update error: {e}")
    
    def on_save_clicked(self):
        try:
            if save_selections(list(self.selected_dates)):
                msg = QMessageBox(self)
                msg.setWindowTitle("✓ Success")
                msg.setText(f"Saved {len(self.selected_dates)} date(s)")
                msg.setIcon(QMessageBox.Information)
                msg.exec()
                logger.info(f"Saved {len(self.selected_dates)} selections")
            else:
                showInfo("Error: Failed to save selections")
        except Exception as e:
            logger.error(f"Save error: {e}", exc_info=True)
            showInfo(f"Error: {str(e)}")
    
    def on_export_clicked(self):
        try:
            if not self.selected_dates:
                msg = QMessageBox(self)
                msg.setWindowTitle("No Selection")
                msg.setText("No dates selected")
                msg.setIcon(QMessageBox.Information)
                msg.exec()
                return
            sorted_dates = sorted(self.selected_dates)
            export_text = "\n".join(sorted_dates)
            clipboard = QApplication.clipboard()
            clipboard.setText(export_text)
            msg = QMessageBox(self)
            msg.setWindowTitle("✓ Exported")
            msg.setText(f"Copied {len(sorted_dates)} date(s)")
            msg.setDetailedText(export_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            logger.info(f"Exported {len(sorted_dates)} dates")
        except Exception as e:
            logger.error(f"Export error: {e}", exc_info=True)
            showInfo(f"Error: {str(e)}")
    
    def on_clear_clicked(self):
        try:
            if not self.selected_dates:
                return
            msg = QMessageBox(self)
            msg.setWindowTitle("Confirm")
            msg.setText(f"Clear {len(self.selected_dates)} date(s)?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setIcon(QMessageBox.Question)
            if msg.exec() == QMessageBox.Ok:
                self.selected_dates.clear()
                self.heatmap_widget.clear_selection()
                self.update_selection_count()
                logger.info("Cleared selections")
        except Exception as e:
            logger.error(f"Clear error: {e}", exc_info=True)
    
    def on_time_range_changed(self, value, checked):
        try:
            if not checked:
                return
            self.time_range = value
            self.review_data = self.fetch_review_data()
            layout = self.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and isinstance(item.widget(), QScrollArea):
                    old_scroll = layout.takeAt(i).widget()
                    old_scroll.deleteLater()
                    break
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            self.heatmap_widget = HeatmapWidget(self.review_data, self)
            self.heatmap_widget.set_selected_dates(self.selected_dates)
            self.heatmap_widget.selection_changed.connect(self.on_selection_changed)
            scroll_area.setWidget(self.heatmap_widget)
            layout.addWidget(scroll_area, 1)
            logger.info(f"Changed range to {value}")
        except Exception as e:
            logger.error(f"Range change error: {e}", exc_info=True)
            showInfo(f"Error: {str(e)}")
    
    def closeEvent(self, event):
        try:
            try:
                self.heatmap_widget.selection_changed.disconnect()
            except:
                pass
            self.selected_dates.clear()
            self.review_data.clear()
            logger.info("Window closed")
        except Exception as e:
            logger.warning(f"Close error: {e}")
        finally:
            super().closeEvent(event)
