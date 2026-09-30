/**
 * Charting components for AegisHealth BRICS Platform using Chart.js
 */

let forecastChartInstance = null;
let federatedChartInstance = null;

function renderForecastChart(data) {
    const ctx = document.getElementById('forecastCanvas');
    if (!ctx) return;

    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    const labels = [...data.historical_dates, ...data.forecast_dates];

    // Historical points (null for forecast period)
    const historicalPoints = [...data.historical_values, ...new Array(data.forecast_dates.length).fill(null)];

    // Forecast points (null for historical period, except overlap at last historical point)
    const forecastPoints = new Array(data.historical_dates.length - 1).fill(null);
    forecastPoints.push(data.historical_values[data.historical_values.length - 1]);
    forecastPoints.push(...data.forecast_values);

    // Lower confidence band
    const lowerBand = new Array(data.historical_dates.length - 1).fill(null);
    lowerBand.push(data.historical_values[data.historical_values.length - 1]);
    lowerBand.push(...data.lower_bounds);

    // Upper confidence band
    const upperBand = new Array(data.historical_dates.length - 1).fill(null);
    upperBand.push(data.historical_values[data.historical_values.length - 1]);
    upperBand.push(...data.upper_bounds);

    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Consumption (Historical)',
                    data: historicalPoints,
                    borderColor: '#38BDF8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: '#0284C7',
                    tension: 0.25,
                    fill: false
                },
                {
                    label: 'AI Forecast Demand (Projected)',
                    data: forecastPoints,
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    pointBackgroundColor: '#D97706',
                    tension: 0.25,
                    fill: false
                },
                {
                    label: 'Upper Confidence (95% CI)',
                    data: upperBand,
                    borderColor: 'rgba(245, 158, 11, 0.25)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: '+1',
                    backgroundColor: 'rgba(245, 158, 11, 0.12)',
                    tension: 0.25
                },
                {
                    label: 'Lower Confidence (95% CI)',
                    data: lowerBand,
                    borderColor: 'rgba(245, 158, 11, 0.25)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.25
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#9CA3AF',
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: '#111827',
                    titleColor: '#F3F4F6',
                    bodyColor: '#E5E7EB',
                    borderColor: '#374151',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9CA3AF',
                        maxTicksLimit: 12
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9CA3AF' },
                    title: {
                        display: true,
                        text: 'Daily Units Consumed',
                        color: '#9CA3AF'
                    }
                }
            }
        }
    });
}

function renderFederatedChart(history) {
    const ctx = document.getElementById('federatedCanvas');
    if (!ctx) return;

    if (federatedChartInstance) {
        federatedChartInstance.destroy();
    }

    const labels = history.map(h => `Round ${h.round_id}`);
    const lossValues = history.map(h => h.global_model_loss);
    const maeValues = history.map(h => h.mean_absolute_error);

    federatedChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'FedAvg Global Loss',
                    data: lossValues,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: '#059669',
                    tension: 0.3,
                    yAxisID: 'y'
                },
                {
                    label: 'Mean Absolute Error (MAE)',
                    data: maeValues,
                    borderColor: '#A78BFA',
                    backgroundColor: 'rgba(167, 139, 250, 0.1)',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#7C3AED',
                    borderDash: [4, 4],
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9CA3AF' }
                },
                tooltip: {
                    backgroundColor: '#111827',
                    borderColor: '#374151',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9CA3AF' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#10B981' },
                    title: { display: true, text: 'Global Loss', color: '#10B981' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#A78BFA' },
                    title: { display: true, text: 'MAE (Units)', color: '#A78BFA' }
                }
            }
        }
    });
}
