#include "../headers/plotter.h"
#include <QDialog>
#include <QLabel>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QDialogButtonBox>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QColorDialog>
#include <QFrame>

AXC1DPlotter::AXC1DPlotter(QWidget* parent)
    : QWidget(parent) {
    setupUI();
    for (int i = 0; i < 3; i++) { createInitialPlot(i + 1); }
}

AXC1DPlotter::~AXC1DPlotter() {
}

void AXC1DPlotter::setupUI() {
    // Main layout for the widget
    QVBoxLayout* mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);
    
    // Create scroll area
    m_scrollArea = new QScrollArea(this);
    m_scrollArea->setWidgetResizable(true);
    m_scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_scrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    
    // Create content widget that will hold all plots
    m_scrollContent = new QWidget();
    m_plotLayout = new QVBoxLayout(m_scrollContent);
    m_plotLayout->setContentsMargins(5, 5, 5, 5);
    m_plotLayout->setSpacing(5);
    m_plotLayout->addStretch();
    
    // Set the content widget in scroll area
    m_scrollArea->setWidget(m_scrollContent);
    
    // Add scroll area to main layout
    mainLayout->addWidget(m_scrollArea);
    
    setLayout(mainLayout);
    setMinimumWidth(750);
}

void AXC1DPlotter::createInitialPlot(int plotNumber) {
    QWidget* plot = new QWidget();
    plot->setMinimumHeight(250);  
    plot->setStyleSheet("border: 2px solid black; background-color: white;");

    // Create a layout FOR this plot widget
    QVBoxLayout* plotLayout = new QVBoxLayout(plot);
    plotLayout->setContentsMargins(10, 10, 10, 10);
    
    QLabel* placeholder = new QLabel(QString("Plot %1").arg(plotNumber));
    placeholder->setAlignment(Qt::AlignCenter);
    placeholder->setStyleSheet("border: none;");
    plotLayout->addWidget(placeholder);
    
    m_plots.append(plot);
    
    // Insert before the stretch
    m_plotLayout->insertWidget(m_plotLayout->count() - 1, plot);
}

void AXC1DPlotter::addPlot() {
    QDialog dialog(this);
    dialog.setWindowTitle("Add New Plot");
    dialog.setFixedSize(450, 320);

    QVBoxLayout* mainLayout = new QVBoxLayout(&dialog);
    
    // Title section
    QLabel* headerLabel = new QLabel("Configurations");
    QFont headerFont = headerLabel->font();
    headerFont.setPointSize(11);
    headerFont.setBold(true);
    headerLabel->setFont(headerFont);
    mainLayout->addWidget(headerLabel);
    
    // Add separator
    QFrame* line = new QFrame();
    line->setFrameShape(QFrame::HLine);
    line->setFrameShadow(QFrame::Sunken);
    mainLayout->addWidget(line);
    
    // Form layout for inputs
    QFormLayout* formLayout = new QFormLayout();
    formLayout->setSpacing(10);
    formLayout->setContentsMargins(10, 10, 10, 10);
    
    // Plot title input
    QLineEdit* titleEdit = new QLineEdit();
    titleEdit->setPlaceholderText("e.g., Temperature vs Time");
    titleEdit->setText(QString("Plot %1").arg(m_plots.count() + 1));
    formLayout->addRow("Plot Title:", titleEdit);
    
    // X-axis label input
    QLineEdit* xLabelEdit = new QLineEdit();
    xLabelEdit->setPlaceholderText("e.g., Time (s)");
    xLabelEdit->setText("X Axis");
    formLayout->addRow("X-Axis Label:", xLabelEdit);
    
    // Y-axis label input
    QLineEdit* yLabelEdit = new QLineEdit();
    yLabelEdit->setPlaceholderText("e.g., Temperature (°C)");
    yLabelEdit->setText("Y Axis");
    formLayout->addRow("Y-Axis Label:", yLabelEdit);
    
    // Line color picker
    QHBoxLayout* colorLayout = new QHBoxLayout();
    QPushButton* colorButton = new QPushButton("Choose Color");
    QLabel* colorPreview = new QLabel();
    colorPreview->setFixedSize(30, 30);
    colorPreview->setStyleSheet("background-color: blue; border: 1px solid black;");
    QColor selectedColor = Qt::blue;
    
    connect(colorButton, &QPushButton::clicked, [&selectedColor, colorPreview]() {
        QColor color = QColorDialog::getColor(selectedColor, nullptr, "Select Line Color");
        if (color.isValid()) {
            selectedColor = color;
            colorPreview->setStyleSheet(QString("background-color: %1; border: 1px solid black;").arg(color.name()));
        }
    });
    
    colorLayout->addWidget(colorButton);
    colorLayout->addWidget(colorPreview);
    colorLayout->addStretch();
    formLayout->addRow("Line Color:", colorLayout);
    
    mainLayout->addLayout(formLayout);
    mainLayout->addStretch();
    
    // Button box
    QDialogButtonBox* buttonBox = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    mainLayout->addWidget(buttonBox);
    
    connect(buttonBox, &QDialogButtonBox::accepted, &dialog, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, &dialog, &QDialog::reject);
    
    if (dialog.exec() == QDialog::Accepted) {
        m_tempTitle = titleEdit->text();
        m_tempXLabel = xLabelEdit->text();
        m_tempYLabel = yLabelEdit->text();
        m_tempLineColor = selectedColor;
        onAddPlotConfirmed();
    }
}

void AXC1DPlotter::deletePlot() {
    // Show dialog for deleting a plot
    QDialog dialog(this);
    dialog.setWindowTitle("Delete Plot");
    dialog.setGeometry(500, 500, 400, 200);

    QVBoxLayout* mainLayout = new QVBoxLayout(&dialog);
    
    // Title section
    QLabel* headerLabel = new QLabel("Configurations");
    QFont headerFont = headerLabel->font();
    headerFont.setPointSize(11);
    headerFont.setBold(true);
    headerLabel->setFont(headerFont);
    mainLayout->addWidget(headerLabel);

    // Add separator
    QFrame* line = new QFrame();
    line->setFrameShape(QFrame::HLine);
    line->setFrameShadow(QFrame::Sunken);
    mainLayout->addWidget(line);
    
    // Form layout for inputs
    QFormLayout* formLayout = new QFormLayout();
    formLayout->setSpacing(10);
    formLayout->setContentsMargins(10, 10, 10, 10);

    QDialogButtonBox* buttonBox = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    mainLayout->addWidget(buttonBox);

    connect(buttonBox, &QDialogButtonBox::accepted, &dialog, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, &dialog, &QDialog::reject);

    if (dialog.exec() == QDialog::Accepted) {
        onDeletePlotConfirmed();
    }
}

void AXC1DPlotter::editPlot() {
    // Show dialog for deleting a plot
    QDialog dialog(this);
    dialog.setWindowTitle("Edit Plot");
    dialog.setGeometry(500, 500, 400, 200);

    QVBoxLayout* layout = new QVBoxLayout(&dialog);
    QLabel* label = new QLabel("Select plot to edit:");
    layout->addWidget(label);

    QDialogButtonBox* buttonBox = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    layout->addWidget(buttonBox);

    connect(buttonBox, &QDialogButtonBox::accepted, &dialog, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, &dialog, &QDialog::reject);

    if (dialog.exec() == QDialog::Accepted) {
        onEditPlotConfirmed();
    }
}

int AXC1DPlotter::getPlotCount() const {
    return m_plots.count();
}

void AXC1DPlotter::onAddPlotConfirmed() {
    // Create new plot widget
    QWidget* plot = new QWidget();
    plot->setMinimumHeight(250);
    plot->setStyleSheet("border: 2px solid black; background-color: white;");
    
    // Create layout for this plot
    QVBoxLayout* plotLayout = new QVBoxLayout(plot);
    plotLayout->setContentsMargins(10, 10, 10, 10);
    
    QLabel* placeholder = new QLabel(QString("Plot %1").arg(m_plots.count() + 1));
    placeholder->setAlignment(Qt::AlignCenter);
    placeholder->setStyleSheet("border: none;");
    plotLayout->addWidget(placeholder);
    
    m_plots.append(plot);
    
    // Insert before the stretch
    m_plotLayout->insertWidget(m_plotLayout->count() - 1, plot);
}

void AXC1DPlotter::onDeletePlotConfirmed() {
    if (m_plots.count() > 1) {  // Keep at least one plot
        QWidget* lastPlot = m_plots.last();
        m_plots.removeLast();
        m_plotLayout->removeWidget(lastPlot);
        lastPlot->deleteLater();
    }
}
void AXC1DPlotter::onEditPlotConfirmed() {}