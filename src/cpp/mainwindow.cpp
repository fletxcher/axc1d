#include "../headers/mainwindow.h"
#include "../headers/textedit.h"
#include "../headers/plotter.h"
#include "../headers/solver.h"

#include <QApplication>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QWidget>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QStatusBar>
#include <QDateTime>
#include <QProgressBar>
#include <QThread>

AXC1DMainWindow::AXC1DMainWindow(QWidget* parent)
    : QMainWindow(parent),
      m_progressBar(nullptr),
      m_timer(nullptr) {

    setWindowTitle("AXC1D");
    setGeometry(500, 500, 1500, 800);
    setFixedSize(1500, 800);

    // Create custom components
    m_editor = std::make_unique<AXC1DTextEditor>();
    m_plotter = std::make_unique<AXC1DPlotter>();
    m_solver = std::make_unique<AXC1DSolver>();

    // Setup menu bar
    createMenuBar();

    // Setup workspace layout
    QWidget* central = new QWidget();
    QHBoxLayout* workspace = new QHBoxLayout(central);
    workspace->addWidget(m_editor.get());
    workspace->addWidget(m_plotter.get());
    setCentralWidget(central);

    // Setup status bar
    createStatusBar();
}

AXC1DMainWindow::~AXC1DMainWindow() {
    if (m_timer) {
        m_timer->stop();
    }
}

void AXC1DMainWindow::createMenuBar() {
    QMenuBar* menuBar = this->menuBar();

    // File Menu
    QMenu* fileMenu = menuBar->addMenu("&File");

    QAction* newFileAction = fileMenu->addAction("&New File");
    newFileAction->setShortcut(Qt::CTRL | Qt::Key_N);
    connect(newFileAction, &QAction::triggered, this, &AXC1DMainWindow::onNewFile);

    QAction* openFileAction = fileMenu->addAction("&Open File");
    openFileAction->setShortcut(Qt::CTRL | Qt::Key_O);
    connect(openFileAction, &QAction::triggered, this, &AXC1DMainWindow::onOpenFile);

    QAction* saveFileAction = fileMenu->addAction("&Save File");
    saveFileAction->setShortcut(Qt::CTRL | Qt::Key_S);
    connect(saveFileAction, &QAction::triggered, this, &AXC1DMainWindow::onSaveFile);

    fileMenu->addSeparator();

    // Plots Menu
    QMenu* plotMenu = menuBar->addMenu("&Plots");

    QAction* addPlotAction = plotMenu->addAction("&Add Plot");
    addPlotAction->setShortcut(Qt::CTRL | Qt::Key_A);
    connect(addPlotAction, &QAction::triggered, this, &AXC1DMainWindow::onAddPlot);

    QAction* deletePlotAction = plotMenu->addAction("&Delete Plot");
    deletePlotAction->setShortcut(Qt::CTRL | Qt::Key_D);
    connect(deletePlotAction, &QAction::triggered, this, &AXC1DMainWindow::onDeletePlot);

    QAction* editPlotAction = plotMenu->addAction("&Edit Plot");
    editPlotAction->setShortcut(Qt::CTRL | Qt::Key_E);
    connect(editPlotAction, &QAction::triggered, this, &AXC1DMainWindow::onEditPlot);

    // Simulations Menu
    QMenu* simulationMenu = menuBar->addMenu("&Simulations");

    QAction* runSimulationAction = simulationMenu->addAction("&Run Simulation");
    runSimulationAction->setShortcut(Qt::CTRL | Qt::Key_R);
    connect(runSimulationAction, &QAction::triggered, this, &AXC1DMainWindow::runSimulation);

    simulationMenu->addSeparator();
    simulationMenu->addAction("&Edit Simulation Path");

    // Settings Menu
    QMenu* settingsMenu = menuBar->addMenu("&Settings");
    settingsMenu->addAction("&Solver Config");

    QAction* exitAction = settingsMenu->addAction("&Exit");
    exitAction->setShortcut(Qt::CTRL | Qt::Key_X);
    connect(exitAction, &QAction::triggered, qApp, &QApplication::quit);
}

void AXC1DMainWindow::createStatusBar() {
    m_timeLabel = new QLabel(this);
    statusBar()->addPermanentWidget(m_timeLabel);

    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &AXC1DMainWindow::updateTime);
    m_timer->start(1000);
    updateTime();
}

void AXC1DMainWindow::updateTime() {
    QString currentTime = QDateTime::currentDateTime().toString("MM/dd/yyyy hh:mm:ss AP");
    m_timeLabel->setText(currentTime);
}

void AXC1DMainWindow::onNewFile() {
    m_editor->newFile();
}

void AXC1DMainWindow::onOpenFile() {
    m_editor->openFileDialog();  // Will be handled by the editor
}

void AXC1DMainWindow::onSaveFile() {
    m_editor->saveFileAsDialog();
}

void AXC1DMainWindow::onAddPlot() {
    m_plotter->addPlot();
}

void AXC1DMainWindow::onDeletePlot() {
    m_plotter->deletePlot();
}

void AXC1DMainWindow::onEditPlot() {
    m_plotter->editPlot();
}

void AXC1DMainWindow::runSimulation() {
    if (!m_progressBar) {
        m_progressBar = new QProgressBar(this);
        statusBar()->addWidget(m_progressBar);
    }

    // Simple progress simulation
    for (int i = 0; i <= 100; ++i) {
        m_progressBar->setValue(i);
        QApplication::processEvents();
        QThread::msleep(50);
    }

    // Small delay before removing
    QThread::sleep(3);

    if (m_progressBar) {
        statusBar()->removeWidget(m_progressBar);
        m_progressBar->deleteLater();
        m_progressBar = nullptr;
    }
}

