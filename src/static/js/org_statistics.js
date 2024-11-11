$(document).ready(function () {
    ordersChart = renderOrdersChart();
    orderStatusChart = renderOrderStatusChart();
    donationsChart = renderDonationsChart();
    ratingsChart = renderRatingsChart();

    $("#donationsFilter").on("change", (event) => {
        event.preventDefault();
    
        const filter = this.value;
        const organization_id = this.getAttribute("data-org-id");
        updateChart(donationsChart, filter, organization_id);
    });
});

function renderOrdersChart() {
    var $ordersChartCtx = $("#ordersChart");
    $.ajax({
        url: $ordersChartCtx.data("url"),
        success: function (data) {
            var ctx = $ordersChartCtx[0].getContext("2d");
            return new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Orders',
                        backgroundColor: '#EEEAF6',
                        borderColor: '#57467B',
                        borderWidth: 1,
                        data: data.data
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false,
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date',
                                font: {
                                    weight: 'bold',
                                    size: 14
                                },
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Order Count',
                                font: {
                                    weight: 'bold',
                                    size: 14
                                },
                            },
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    });
}

function renderOrderStatusChart() {
    var $orderStatusChartCtx = $("#orderSuccessChart");
    $.ajax({
        url: $orderStatusChartCtx.data("url"),
        success: function (data) {
            var ctx = $orderStatusChartCtx[0].getContext("2d");
            return new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Order Statuses',
                        data: data.data,
                        backgroundColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 205, 86)',
                            'rgb(255, 99, 132)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (data) {
                                    return `${data.label} Orders: ${data.raw}`;
                                }
                            }
                        }
                    },
                }
            });
        }
    });
}

function renderDonationsChart() {
    var $donationsChartCtx = $("#donationsChart");
    $.ajax({
        url: $donationsChartCtx.data("url"),
        success: function (data) {
            var ctx = $donationsChartCtx[0].getContext("2d");
            return new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Donations',
                        backgroundColor: '#EEEAF6',
                        borderColor: '#57467B',
                        borderWidth: 1,
                        data: data.data
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false,
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date',
                                font: {
                                    weight: 'bold',
                                    size: 14
                                },
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Donation Count',
                                font: {
                                    weight: 'bold',
                                    size: 14
                                },
                            },
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    });
}

function renderRatingsChart() {
    var $ratingsChartCtx = $("#ratingsChart");
    $.ajax({
        url: $ratingsChartCtx.data("url"),
        success: function (data) {
            var ctx = $ratingsChartCtx[0].getContext("2d");
            return new Chart(ctx, {
                type: "polarArea",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Ratings',
                        data: data.data,
                        backgroundColor: [
                            'rgb(201, 203, 207)',
                            'rgb(255, 99, 132)',
                            'rgb(255, 205, 86)',
                            'rgb(54, 162, 235)',
                            'rgb(75, 192, 192)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        r: {
                            pointLabels: {
                                display: true,
                                centerPointLabels: true,
                                font: {
                                    size: 14
                                }
                            },
                            ticks: {
                                beginAtZero: true
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 30
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (data) {
                                    return `Rating ${data.label}: ${data.raw}`;
                                }
                            }
                        }
                    },
                }
            });
        }
    });
}

function updateChart(chart, filter, organization_id) {
    params = {"filter": filter}
    endpoint = reverse("donor_dashboard:statistics_filter", args=[organization_id]) + "?" + urlencode(params)
    $.ajax({
        url: endpoint,
        success: function (data) {
            chart.data.labels = [];
            chart.data.datasets = [];
            chart.data.labels = data.labels;
            chart.data.datasets[0].data = data.data;
            chart.update();
        }
    })
}

document.getElementById("donationsFilter").addEventListener("change", function() {
    const filter = this.value;
    const organization_id = this.getAttribute("data-org-id");
    updateChart(donationsChart, filter, organization_id);
});
