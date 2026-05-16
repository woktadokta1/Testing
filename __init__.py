import sys
import os
import logging
from aqt import mw
from aqt.qt import *

addon_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(addon_dir, "debug.log")
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    if addon_dir not in sys.path:
        sys.path.insert(0, addon_dir)
    from heatmap_window import HeatmapWindow
    logger.info("Addon initialized")
except Exception as e:
    logger.error(f"Init error: {e}", exc_info=True)

def show_heatmap_window():
    try:
        dialog = HeatmapWindow(mw)
        dialog.exec()
    except Exception as e:
        logger.error(f"Window error: {e}", exc_info=True)
        try:
            from aqt.utils import showInfo
            showInfo(f"Error: {str(e)}")
        except:
            pass

try:
    action = QAction("Show Review Heatmap", mw)
    action.triggered.connect(show_heatmap_window)
    mw.form.menuTools.addAction(action)
except Exception as e:
    logger.error(f"Menu error: {e}", exc_info=True)
