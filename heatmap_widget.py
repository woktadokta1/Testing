import datetime
import logging
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)

try:
    from aqt.qt import *
except Exception as e:
    logger.error(f"Qt import error: {e}")
    raise

class HeatmapWidget(QWidget):
    selection_changed = pyqtSignal()
    
    def __init__(self, review_data: Dict[str, int], parent=None):
        super().__init__(parent)
        try:
            self.review_data = review_data if review_data else {}
            self.selected_dates: Set[str] = set()
            self.hovered_date: Optional[str] = None
            
            if self.review_data:
                try:
                    dates = sorted(self.review_data.keys())
                    if dates:
                        self.start_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d").date()
                        self.end_date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d").date()
                    else:
                        raise ValueError("Empty dates")
                except (ValueError, IndexError):
                    self.end_date = datetime.date.today()
                    self.start_date = self.end_date - datetime.timedelta(days=1095)
            else:
                self.end_date = datetime.date.today()
                self.start_date = self.end_date - datetime.timedelta(days=1095)
            
            self.cell_size = 18
            self.spacing = 3
            self.padding = 60
            self.top_padding = 40
            
            self.setMouseTracking(True)
            self.setCursor(Qt.PointingHandCursor)
            self.update_size_hint()
        except Exception as e:
            logger.error(f"Widget init error: {e}", exc_info=True)
            raise
    
    def set_selected_dates(self, dates: Set[str]):
        try:
            validated = set()
            for date_str in dates:
                try:
                    datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    validated.add(date_str)
                except ValueError:
                    logger.warning(f"Invalid date: {date_str}")
            self.selected_dates = validated
            self.update()
        except Exception as e:
            logger.error(f"Set dates error: {e}")
    
    def get_selected_dates(self):
        return self.selected_dates.copy()
    
    def clear_selection(self):
        self.selected_dates.clear()
        self.update()
    
    def toggle_date(self, date_str: str):
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if date_str in self.selected_dates:
                self.selected_dates.remove(date_str)
            else:
                self.selected_dates.add(date_str)
            self.selection_changed.emit()
            self.update()
        except ValueError as e:
            logger.warning(f"Toggle date error: {date_str}: {e}")
    
    def date_from_pos(self, x: int, y: int):
        try:
            x -= self.padding
            y -= self.top_padding
            if x < 0 or y < 0:
                return None
            week = x // (self.cell_size + self.spacing)
            day = y // (self.cell_size + self.spacing)
            if week < 0 or day < 0 or day > 6:
                return None
            first_week_day = self.start_date.weekday()
            days_offset = week * 7 + day - first_week_day
            date = self.start_date + datetime.timedelta(days=days_offset)
            if date < self.start_date or date > self.end_date:
                return None
            date_str = date.strftime("%Y-%m-%d")
            return date_str if date_str in self.review_data else None
        except Exception as e:
            logger.warning(f"Date from pos error: {e}")
            return None
    
    def paintEvent(self, event: QPaintEvent):
        try:
            painter = QPainter(self)
            if not painter.isActive():
                return
            painter.setRenderHint(QPainter.Antialiasing)
            
            values = [v for v in self.review_data.values() if v > 0]
            min_val = min(values) if values else 0
            max_val = max(values) if values else 1
            if max_val == 0:
                max_val = 1
            
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.setFont(QFont("Arial", 9))
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, day in enumerate(days):
                y = self.top_padding + i * (self.cell_size + self.spacing) + self.cell_size // 2
                painter.drawText(0, y, self.padding - 5, self.cell_size, Qt.AlignRight | Qt.AlignVCenter, day)
            
            current_date = self.start_date
            last_month = -1
            first_week_day = self.start_date.weekday()
            
            while current_date <= self.end_date:
                if current_date.month != last_month and current_date.day <= 7:
                    days_diff = (current_date - self.start_date).days
                    adjusted_days = days_diff + first_week_day
                    week = adjusted_days // 7
                    x = self.padding + week * (self.cell_size + self.spacing)
                    month_name = current_date.strftime("%b")
                    painter.drawText(x, 15, self.cell_size * 2, 20, Qt.AlignCenter, month_name)
                    last_month = current_date.month
                current_date += datetime.timedelta(days=1)
            
            current_date = self.start_date
            first_week_day = self.start_date.weekday()
            
            while current_date <= self.end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str in self.review_data:
                    days_diff = (current_date - self.start_date).days
                    adjusted_days = days_diff + first_week_day
                    week = adjusted_days // 7
                    day = adjusted_days % 7
                    x = self.padding + week * (self.cell_size + self.spacing)
                    y = self.top_padding + day * (self.cell_size + self.spacing)
                    
                    value = self.review_data[date_str]
                    if value == 0:
                        color = QColor(230, 230, 230)
                    else:
                        intensity = int(50 + (value - min_val) * 205 / (max_val - min_val))
                        intensity = max(50, min(255, intensity))
                        red = max(0, min(255, 100 - int(intensity * 0.3)))
                        green = max(0, min(255, 120 - int(intensity * 0.2)))
                        blue = max(0, min(255, 150 + int(intensity * 0.3)))
                        color = QColor(red, green, blue)
                    
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(QColor(200, 200, 200), 1))
                    painter.drawRect(x, y, self.cell_size, self.cell_size)
                    
                    if date_str in self.selected_dates:
                        painter.setBrush(Qt.NoBrush)
                        painter.setPen(QPen(QColor(0, 0, 0), 3))
                        painter.drawRect(x, y, self.cell_size, self.cell_size)
                    
                    if date_str == self.hovered_date:
                        painter.setBrush(Qt.NoBrush)
                        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
                        painter.drawRect(x - 1, y - 1, self.cell_size + 2, self.cell_size + 2)
                
                current_date += datetime.timedelta(days=1)
            
            painter.end()
        except Exception as e:
            logger.error(f"Paint error: {e}", exc_info=True)
    
    def mousePressEvent(self, event: QMouseEvent):
        try:
            if event.button() == Qt.LeftButton:
                date_str = self.date_from_pos(event.x(), event.y())
                if date_str:
                    self.toggle_date(date_str)
            elif event.button() == Qt.RightButton:
                self.show_context_menu(event.pos())
        except Exception as e:
            logger.error(f"Mouse press error: {e}", exc_info=True)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            date_str = self.date_from_pos(event.x(), event.y())
            if date_str != self.hovered_date:
                self.hovered_date = date_str
                self.update()
        except Exception as e:
            logger.warning(f"Mouse move error: {e}")
    
    def leaveEvent(self, event: QEvent):
        try:
            self.hovered_date = None
            self.update()
        except Exception as e:
            logger.warning(f"Leave error: {e}")
    
    def show_context_menu(self, pos: QPoint):
        try:
            date_str = self.date_from_pos(pos.x(), pos.y())
            if not date_str:
                return
            menu = QMenu(self)
            action = menu.addAction("Deselect Date" if date_str in self.selected_dates else "Select Date")
            menu.addSeparator()
            action_clear = menu.addAction("Clear All")
            result = menu.exec(self.mapToGlobal(pos))
            if result == action:
                self.toggle_date(date_str)
            elif result == action_clear:
                self.clear_selection()
                self.selection_changed.emit()
        except Exception as e:
            logger.error(f"Context menu error: {e}", exc_info=True)
    
    def update_size_hint(self):
        try:
            days_diff = (self.end_date - self.start_date).days
            first_week_day = self.start_date.weekday()
            weeks = (days_diff + first_week_day) // 7 + 1
            width = self.padding + weeks * (self.cell_size + self.spacing) + 20
            height = self.top_padding + 7 * (self.cell_size + self.spacing) + 20
            self.setMinimumSize(width, height)
        except Exception as e:
            logger.warning(f"Size hint error: {e}")
    
    def sizeHint(self):
        try:
            days_diff = (self.end_date - self.start_date).days
            first_week_day = self.start_date.weekday()
            weeks = (days_diff + first_week_day) // 7 + 1
            width = self.padding + weeks * (self.cell_size + self.spacing) + 20
            height = self.top_padding + 7 * (self.cell_size + self.spacing) + 20
            return QSize(width, height)
        except Exception as e:
            logger.warning(f"Size hint error: {e}")
            return QSize(1000, 300)
    
    def closeEvent(self, event):
        try:
            self.selected_dates.clear()
            self.hovered_date = None
        except Exception as e:
            logger.warning(f"Close error: {e}")
