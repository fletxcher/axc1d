import logging 
from PyQt6.QtCore import Qt
from manager import AXC1DEventManager
from PyQt6.QtGui import QColor, QTextFormat
from PyQt6.QtWidgets import  QTextEdit, QFileDialog
from PyQt6.QtGui import QKeySequence, QShortcut

class AXC1DTextEditor(QTextEdit):
    def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager, parent = None):
        super().__init__(parent)
        self.logger = logger
        self.event_manager = event_manager
        # enable the undo and redo feature
        self.setUndoRedoEnabled(True)
        # zoom-in and zoom-out functionality
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)
        # connect the cursor position changed signal to the highlight slot
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.highlight_current_line() # Highlight the initial line

    def highlight_current_line(self):
        # create a list to hold extra selections
        extra_selections = []

        # define the selection format (e.g., light gray background)
        selection = QTextEdit.ExtraSelection()
        line_color = QColor(Qt.GlobalColor.lightGray).lighter(110) # Adjust color as needed
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True) # Highlight full width

        # eet the cursor to the current line
        cursor = self.textCursor()
        # ensure no text is selected initially for this operation
        cursor.clearSelection() 
        selection.cursor = cursor

        # append the selection to the list
        extra_selections.append(selection)

        # apply the extra selections
        self.setExtraSelections(extra_selections)

    def open_file(self):
        # read in the file path from the file dialog, open the file, and fill the text editor with the files contents 
        self.file_path = QFileDialog.getOpenFileName(self, "Open File", "~", "All files (*)")[0]
        with open(self.file_path, "r") as f:
            content = f.read()
            self.setText(content)
        f.close()
        self.event_manager.emit("open_file")

    def new_file(self):
        # open a new completely blank input deck
        pass

    def save_file(self):
        # save the current file
        content = self.toPlainText()
        self.logger.info(f"Content: {content}")

    def zoom_in(self):
        self.zoomIn(1) 

    def zoom_out(self):
        self.zoomOut(1)