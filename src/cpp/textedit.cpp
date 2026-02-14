#include "../headers/textedit.h"
#include <QFile>
#include <QTextStream>
#include <QFileDialog>
#include <QMessageBox>

AXC1DTextEditor::AXC1DTextEditor(QWidget* parent)
    : QPlainTextEdit(parent), m_fontSize(10) {
    setUndoRedoEnabled(true);
    setupConnections();
    highlightCurrentLine();
}

AXC1DTextEditor::~AXC1DTextEditor() {
}

QString AXC1DTextEditor::getCurrentFilePath() const {
    return m_currentFilePath;
}

bool AXC1DTextEditor::openFile(const QString& filepath) {
    if (filepath.isEmpty()) {
        return false;
    }

    QFile file(filepath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QMessageBox::warning(this, "Error", 
            "Could not open file: " + filepath);
        return false;
    }

    QTextStream in(&file);
    QString content = in.readAll();
    setPlainText(content);

    m_currentFilePath = filepath;
    file.close();
    return true;
}

bool AXC1DTextEditor::openFileDialog() {
    QString filepath = QFileDialog::getOpenFileName(
        this,                                    // parent
        "Open File",                             // dialog title
        QString(),                               // starting directory (empty = last used)
        "All Files (*.*)"                        // file filters
    );

    if (filepath.isEmpty()) {
        return false;  // User cancelled
    }

    return openFile(filepath);
}

bool AXC1DTextEditor::saveFile() {
    if (m_currentFilePath.isEmpty()) {
        return saveFileAsDialog();  // No file path, ask user
    }

    QFile file(m_currentFilePath);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QMessageBox::warning(this, "Error", 
            "Could not save file: " + m_currentFilePath);
        return false;
    }

    QTextStream out(&file);
    out << toPlainText();
    file.close();
    return true;
}

bool AXC1DTextEditor::saveFileAs(const QString& filepath) {
    if (filepath.isEmpty()) {
        return false;
    }

    m_currentFilePath = filepath;
    return saveFile();
}

bool AXC1DTextEditor::saveFileAsDialog() {
    QString filepath = QFileDialog::getSaveFileName(
        this,                                    // parent
        "Save File As",                          // dialog title
        QString(),                               // starting directory
        "All Files (*.*)"                        // file filters
    );

    if (filepath.isEmpty()) {
        return false;  // User cancelled
    }

    return saveFileAs(filepath);
}

bool AXC1DTextEditor::newFile() {
    clear();
    m_currentFilePath = QString();
    return true;
}

void AXC1DTextEditor::keyPressEvent(QKeyEvent* event) {
    if (event->modifiers() & Qt::ControlModifier) {
        if (event->key() == Qt::Key_Plus || event->key() == Qt::Key_Equal) {
            m_fontSize++;
            QFont font = this->font();
            font.setPointSize(m_fontSize);
            setFont(font);
            return;
        } else if (event->key() == Qt::Key_Minus) {
            m_fontSize--;
            QFont font = this->font();
            font.setPointSize(m_fontSize);
            setFont(font);
            return;
        }
    }
    QPlainTextEdit::keyPressEvent(event);
}

void AXC1DTextEditor::wheelEvent(QWheelEvent* event) {
    if (event->modifiers() & Qt::ControlModifier) {
        if (event->angleDelta().y() > 0) {
            m_fontSize++;
        } else {
            m_fontSize--;
        }
        QFont font = this->font();
        font.setPointSize(m_fontSize);
        setFont(font);
        event->accept();
    } else {
        QPlainTextEdit::wheelEvent(event);
    }
}

void AXC1DTextEditor::setupConnections() {
    connect(this, &QPlainTextEdit::cursorPositionChanged,
            this, &AXC1DTextEditor::highlightCurrentLine);
}

void AXC1DTextEditor::highlightCurrentLine() {
    applyLineHighlight();
}

void AXC1DTextEditor::applyLineHighlight() {
    QList<QTextEdit::ExtraSelection> extraSelections;

    if (!isReadOnly()) {
        QTextEdit::ExtraSelection selection;
        QColor lineColor = QColor(Qt::lightGray).lighter(110);
        selection.format.setBackground(lineColor);
        selection.format.setProperty(QTextFormat::FullWidthSelection, true);
        selection.cursor = textCursor();
        selection.cursor.clearSelection();
        extraSelections.append(selection);
    }

    setExtraSelections(extraSelections);
}