# ui/models.py
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from ui.i18n import Translator


class ClipHistoryModel(QAbstractTableModel):
    """历史记录表格模型，支持动态语言切换。"""

    def __init__(self, records=None, translator: Translator | None = None, parent=None):
        super().__init__(parent)
        self._records = records or []
        self._translator = translator or Translator()
        self._headers = []
        self._update_headers()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._records)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._records)):
            return None
        record = self._records[index.row()]
        if role == Qt.DisplayRole:
            column_map = {
                0: record.get("timestamp_display", ""),
                1: record.get("app", ""),
                2: record.get("category", ""),
                3: record.get("types_display", ""),
                4: record.get("masked_preview", ""),
            }
            return column_map.get(index.column(), "")
        if role == Qt.TextAlignmentRole and index.column() in (0, 1, 2, 3):
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
        return super().headerData(section, orientation, role)

    def set_records(self, records):
        self.beginResetModel()
        self._records = list(records) if records else []
        self.endResetModel()

    def add_record(self, record):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._records.insert(0, record)
        self.endInsertRows()

    def record_at(self, row):
        if 0 <= row < len(self._records):
            return self._records[row]
        return None

    def remove_by_id(self, record_id):
        for idx, record in enumerate(self._records):
            if record.get("id") == record_id:
                self.beginRemoveRows(QModelIndex(), idx, idx)
                self._records.pop(idx)
                self.endRemoveRows()
                return True
        return False

    def all_records(self):
        return list(self._records)

    def set_translator(self, translator: Translator):
        self._translator = translator
        self._update_headers()
        if self.columnCount() > 0:
            self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount() - 1)

    def _update_headers(self):
        self._headers = [
            self._tr("table.column.time"),
            self._tr("table.column.app"),
            self._tr("table.column.category"),
            self._tr("table.column.sensitive"),
            self._tr("table.column.masked"),
        ]

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)
