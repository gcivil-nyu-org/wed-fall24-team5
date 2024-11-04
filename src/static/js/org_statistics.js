$(document).ready(function () {
    renderOrdersChart();
    renderOrderStatusChart();
    renderDonationsChart();
    renderRatingsChart();
});

function renderOrdersChart() {
    var $ordersChart = $("#ordersChart");
    $.ajax({
        url: $ordersChart.data("url"),
        success: function (data) {
            var ctx = $ordersChart[0].getContext("2d");
            new Chart(ctx, {
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
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Order Count'
                            }
                        }
                    }
                }
            });
        }
    });
}

function renderOrderStatusChart() {
    var $orderSuccessChart = $("#orderSuccessChart");
    $.ajax({
        url: $orderSuccessChart.data("url"),
        success: function (data) {
            var ctx = $orderSuccessChart[0].getContext("2d");
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Order Statuses',
                        data: data.data
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(data) {
                                    return `${data.label}: ${data.raw}`;
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
    var $donationsChart = $("#donationsChart");
    $.ajax({
        url: $donationsChart.data("url"),
        success: function (data) {
            var ctx = $donationsChart[0].getContext("2d");
            new Chart(ctx, {
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
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Donation Count'
                            }
                        }
                    }
                }
            });
        }
    });
}

function renderRatingsChart() {
    var $ratingsChart = $("#ratingsChart");
    $.ajax({
        url: $ratingsChart.data("url"),
        success: function (data) {
            var ctx = $ratingsChart[0].getContext("2d");
            new Chart(ctx, {
                type: "polarArea",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Ratings',
                        data: data.data
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
                          }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(data) {
                                    return `${data.label}: ${data.raw}`;
                                }
                            }
                        }
                    },
                }
            });
        }
    });
}

// const organization_id = "{{ organization_id }}";

// $(document).ready(function () {
//     $.ajax({
//         url: "/donor_dashboard/statistics/filter_statistics/",
//         type: "GET",
//         dataType: "json",
//         success: (jsonResponse) => {
//             // Load all the options
//             jsonResponse.options.forEach(option => {
//                 $("#month").append(new Option(option, option));
//             });
//             // Load data for the first option
//             loadAllCharts($("#month").children().first().val());
//         },
//         error: () => console.log("Failed to fetch chart filter options!")
//     });
// });

// $("#filterForm").on("submit", (event) => {
//     event.preventDefault();

//     const month = $("#month").val();
//     loadAllCharts(month)
// });

// function loadChart(chart, endpoint) {
//     $.ajax({
//         url: endpoint,
//         type: "GET",
//         dataType: "json",
//         success: (jsonResponse) => {
//             // Extract data from the response
//             const title = jsonResponse.title;
//             const labels = jsonResponse.data.labels;
//             const datasets = jsonResponse.data.datasets;

//             // Reset the current chart
//             chart.data.datasets = [];
//             chart.data.labels = [];

//             // Load new data into the chart
//             chart.options.title.text = title;
//             chart.options.title.display = true;
//             chart.data.labels = labels;
//             datasets.forEach(dataset => {
//                 chart.data.datasets.push(dataset);
//             });
//             chart.update();
//         },
//         error: () => console.log("Failed to fetch chart data from " + endpoint + "!")
//     });
// }

// function loadAllCharts(month) {
//     loadChart(ordersChart, `/donor_dashboard/statistics/${organization_id}/orders/${month}/`);
// }
