document.addEventListener('DOMContentLoaded', (event) => {
    var ctx1 = document.getElementById('productClassChart').getContext('2d');
    var ctx2 = document.getElementById('productDepartmentChart').getContext('2d');
    var ctx3 = document.getElementById('posNegPieChart').getContext('2d');
  

    var productClassLabels = productClassData.map(item => item[0]);
    var productClassValues = productClassData.map(item => item[1]);

    var productDepartmentLabels = productDepartmentData.map(item => item[0]);
    var productDepartmentValues = productDepartmentData.map(item => item[1]);

    var posNegLabels = positiveNegativeData.map(item => item[0]);
    const posNegcounts = positiveNegativeData.map(item => item[1]);
    console.log(posNegcounts);
    const totalCount = posNegcounts.reduce((total, count) => total + count, 0);

    // Calculate percentages
    const percentages = posNegcounts.map(count => Math.round((count / totalCount) * 100));

    console.log(percentages); // Output: Array of percentages



    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: productClassLabels,
            datasets: [{
                label: 'Positive Index',
                data: productClassValues,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: productDepartmentLabels,
            datasets: [{
                label: 'Positive Index',
                data: productDepartmentValues,
                backgroundColor: [
                    'rgba(153, 102, 255, 0.2)',
                    // 'rgba(255, 99, 132, 0.2)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    // 'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    new Chart(ctx3,
        {
            type: 'pie',
            data: {
                labels: posNegLabels,
                datasets: [{
                    data: percentages,
                    backgroundColor: [
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 99, 132, 0.2)',
                    ],
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Distribution of sentimental %'
                    }
                }
            },
        }
    );



});
