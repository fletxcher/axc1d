#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include <QLabel>
#include <QProgressBar>
#include <memory>

class AXC1DTextEditor;
class AXC1DPlotter;
class AXC1DSolver;

/**
 * Main window for AXC1D multistage compressor analysis application
 */
class AXC1DMainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit AXC1DMainWindow(QWidget* parent = nullptr);
    ~AXC1DMainWindow();

private slots:
    void updateTime();
    void runSimulation();
    void onNewFile();
    void onOpenFile();
    void onSaveFile();
    void onAddPlot();
    void onDeletePlot();
    void onEditPlot();

private:
    void setupUI();
    void createMenuBar();
    void createStatusBar();

    std::unique_ptr<AXC1DTextEditor> m_editor;
    std::unique_ptr<AXC1DPlotter> m_plotter;
    std::unique_ptr<AXC1DSolver> m_solver;

    QLabel* m_timeLabel;
    QProgressBar* m_progressBar;
    QTimer* m_timer;
};

#endif // MAINWINDOW_H
