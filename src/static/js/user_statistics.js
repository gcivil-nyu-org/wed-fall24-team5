$(document).ready(function () {
    renderUserOrdersChart();
    renderUserDonationsChart();
});

function renderUserOrdersChart() {
    var $userOrdersChartCtx = $("#userOrdersChart");
    $.ajax({
        url: $userOrdersChartCtx.data("url"),
        success: function (data) {
            var ctx = $userOrdersChartCtx[0].getContext("2d");
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

function renderUserDonationsChart() {
    var $userDonationsChartCtx = $("#userDonationsChart");
    $.ajax({
        url: $userDonationsChartCtx.data("url"),
        success: function (data) {
            var ctx = $userDonationsChartCtx[0].getContext("2d");
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
