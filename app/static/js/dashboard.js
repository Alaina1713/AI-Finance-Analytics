// Price Trend Chart
const ctx1 = document.getElementById('priceChart').getContext('2d');
new Chart(ctx1, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{
            label: 'Price (USD)',
            data: [120, 125, 130, 128, 135],
            borderColor: '#00c6ff',
            backgroundColor: 'rgba(0, 198, 255, 0.2)',
            tension: 0.3,
            fill: true
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { labels: { color: "#fff" } } },
        scales: {
            x: { ticks: { color: "#fff" } },
            y: { ticks: { color: "#fff" } }
        }
    }
});

// Anomaly Detection
const ctx2 = document.getElementById('anomalyChart').getContext('2d');
new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Txn1', 'Txn2', 'Txn3', 'Txn4'],
        datasets: [{
            label: 'Anomaly Score',
            data: [0.1, 0.9, 0.2, 0.8],
            backgroundColor: ['#00c6ff', '#ff3d67', '#00c6ff', '#ff3d67']
        }]
    },
    options: {
        plugins: { legend: { labels: { color: "#fff" } } },
        scales: {
            x: { ticks: { color: "#fff" } },
            y: { ticks: { color: "#fff" } }
        }
    }
});

// Sentiment Chart
const ctx3 = document.getElementById('sentimentChart').getContext('2d');
new Chart(ctx3, {
    type: 'doughnut',
    data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
            label: 'Sentiment',
            data: [60, 25, 15],
            backgroundColor: ['#00c6ff', '#ffaa00', '#ff3d67']
        }]
    },
    options: {
        plugins: { legend: { labels: { color: "#fff" } } }
    }
});

// Forecast Chart
const ctx4 = document.getElementById('forecastChart').getContext('2d');
new Chart(ctx4, {
    type: 'line',
    data: {
        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
        datasets: [{
            label: 'Forecasted Price',
            data: [140, 145, 150, 152, 158],
            borderColor: '#ffaa00',
            backgroundColor: 'rgba(255,170,0,0.2)',
            tension: 0.3,
            fill: true
        }]
    },
    options: {
        plugins: { legend: { labels: { color: "#fff" } } },
        scales: {
            x: { ticks: { color: "#fff" } },
            y: { ticks: { color: "#fff" } }
        }
    }
});
