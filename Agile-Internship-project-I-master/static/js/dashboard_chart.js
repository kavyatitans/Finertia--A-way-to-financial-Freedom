// dashboard_chart.js

document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('spendingChart').getContext('2d');
    var categories = JSON.parse(document.getElementById('categories-data').textContent);
    var amounts = JSON.parse(document.getElementById('amounts-data').textContent);

    var chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)',
                    'rgba(40, 159, 64, 0.8)',
                    'rgba(210, 199, 199, 0.8)',
                ],
            }]
        },
        options: {
    responsive: true,
    title: {
        display: true,
        text: 'Spending by Category'
    },
    legend: {
        display: true,
        position: 'bottom'
    }
}
    });
});
