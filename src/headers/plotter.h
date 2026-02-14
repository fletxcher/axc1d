#ifndef PLOTTER_H
#define PLOTTER_H

#include <QWidget>
#include <QVBoxLayout>
#include <QScrollArea>
#include <QList>

/**
 * Plotter widget for AXC1D providing data visualization
 */
class AXC1DPlotter : public QWidget {
    Q_OBJECT

public:
    explicit AXC1DPlotter(QWidget* parent = nullptr);
    ~AXC1DPlotter();

    void addPlot();
    void editPlot();
    void deletePlot();
    int getPlotCount() const;

private slots:
    void onAddPlotConfirmed();
    void onDeletePlotConfirmed();
    void onEditPlotConfirmed();

private:
    void setupUI();
    void createInitialPlot(int numPlots);

    QScrollArea* m_scrollArea;           
    QWidget* m_scrollContent;            
    QVBoxLayout* m_plotLayout;
    QList<QWidget*> m_plots;
    
    // Store dialog input temporarily
    QString m_tempTitle;
    QString m_tempXLabel;
    QString m_tempYLabel;
    QColor m_tempLineColor;
    int m_tempPlotIndex;
};

#endif // PLOTTER_H