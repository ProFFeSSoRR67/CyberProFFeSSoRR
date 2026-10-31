
async function loadStats() {
    try {
        const response = await fetch("/api/stats");

        if (!response.ok) {
            throw new Error("Ошибка загрузки статистики");
        }

        const data = await response.json();

        const format = (value) => {
            if (value === null || value === undefined) {
                return "—";
            }

            return Number(value).toLocaleString("ru-RU");
        };

        document.getElementById("subscribers").textContent =
            format(data.subscribers);

        document.getElementById("videos").textContent =
            format(data.videos);

        document.getElementById("total-views").textContent =
            format(data.total_views);

        console.log("Статистика YouTube загружена");

    } catch (error) {
        console.error("Ошибка:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadStats);

async function loadAnalytics() {
    const message = document.getElementById("chart-message");

    try {
        const response = await fetch("/api/analytics");

        if (!response.ok) {
            throw new Error("Отчёт пока недоступен");
        }

        const data = await response.json();

        const format = (value) =>
            Number(value).toLocaleString("ru-RU");

        document.getElementById("views-28").textContent =
            format(data.views_28);

        document.getElementById("watch-time").textContent =
            format(data.watch_hours_28) + " ч";

        if (!data.daily || data.daily.length === 0) {
            message.textContent =
                "YouTube пока не вернул данные за этот период";
            return;
        }

        const labels = data.daily.map(item => item.date);
        const views = data.daily.map(item => item.views);

        new Chart(
            document.getElementById("viewsChart"),
            {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Просмотры",
                        data: views,
                        borderColor: "#e6c78b",
                        backgroundColor: "rgba(230,199,139,0.12)",
                        borderWidth: 3,
                        pointRadius: 3,
                        pointBackgroundColor: "#ffe3a5",
                        tension: 0.35,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: "#e6c78b"
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: "#9eafc5",
                                maxTicksLimit: 7
                            },
                            grid: {
                                color: "rgba(230,199,139,0.08)"
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: "#9eafc5"
                            },
                            grid: {
                                color: "rgba(230,199,139,0.1)"
                            }
                        }
                    }
                }
            }
        );

        message.textContent =
            "Последний день с данными: " +
            data.last_data_date;

    } catch (error) {
        console.error(error);
        message.textContent =
            "Не удалось загрузить график";
    }
}

document.addEventListener(
    "DOMContentLoaded",
    loadAnalytics
);

