#ifndef TEXTEDIT_H
#define TEXTEDIT_H

#include <QPlainTextEdit>
#include <QString>

/**
 * Custom text editor for AXC1D with syntax highlighting and file operations
 */
class AXC1DTextEditor : public QPlainTextEdit {
    Q_OBJECT

public:
    explicit AXC1DTextEditor(QWidget* parent = nullptr);
    ~AXC1DTextEditor();

    QString getCurrentFilePath() const;
    bool openFile(const QString& filepath);
    bool openFileDialog();
    bool saveFile();
    bool saveFileAs(const QString& filepath);
    bool saveFileAsDialog();
    bool newFile();

protected:
    void keyPressEvent(QKeyEvent* event) override;
    void wheelEvent(QWheelEvent* event) override;

private slots:
    void highlightCurrentLine();

private:
    void setupConnections();
    void applyLineHighlight();

    QString m_currentFilePath;
    int m_fontSize;
};

#endif // TEXTEDIT_H
