
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


let analyticsChart = null;
let analyticsData = null;

function formatNumber(value) {
    return Number(value).toLocaleString("ru-RU");
}

function showChart(type) {
    if (!analyticsData || !analyticsData.daily.length) {
        return;
    }

    const isSubscribers = type === "subscribers";

    const labels = analyticsData.daily.map(
        item => item.date
    );

    const values = analyticsData.daily.map(
        item => isSubscribers
            ? item.subscribers_net
            : item.views
    );

    const color = isSubscribers
        ? "#38f5e0"
        : "#ffd36e";

    const fillColor = isSubscribers
        ? "rgba(56,245,224,0.12)"
        : "rgba(255,211,110,0.14)";

    document.getElementById("chart-title").textContent =
        isSubscribers
            ? "Динамика подписчиков"
            : "Путешествие просмотров";

    document.querySelectorAll(".chart-tab").forEach(
        button => {
            button.classList.toggle(
                "active",
                button.dataset.chart === type
            );
        }
    );

    if (analyticsChart) {
        analyticsChart.destroy();
    }

    const ctx = document.getElementById("viewsChart");

    analyticsChart = new Chart(ctx, {
        type: isSubscribers ? "bar" : "line",

        data: {
            labels: labels,
            datasets: [{
                label: isSubscribers
                    ? "Чистый прирост подписчиков"
                    : "Просмотры",

                data: values,

                borderColor: color,
                backgroundColor: fillColor,
                borderWidth: isSubscribers ? 1 : 3,

                pointRadius: isSubscribers ? 0 : 4,
                pointHoverRadius: 7,
                pointBackgroundColor: color,

                tension: 0.25,
                fill: !isSubscribers,

                borderRadius: isSubscribers ? 4 : 0
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            animation: {
                duration: 650
            },

            interaction: {
                mode: "index",
                intersect: false
            },

            plugins: {
                legend: {
                    labels: {
                        color: "#f5f0e7",
                        font: {
                            size: 13
                        }
                    }
                },

                tooltip: {
                    backgroundColor: "#071322",
                    titleColor: "#ffe3a5",
                    bodyColor: "#ffffff",
                    borderColor: color,
                    borderWidth: 1,

                    callbacks: {
                        label: context => {
                            const value = context.parsed.y;

                            if (isSubscribers) {
                                return " Прирост: " +
                                    (value > 0 ? "+" : "") +
                                    formatNumber(value);
                            }

                            return " Просмотры: " +
                                formatNumber(value);
                        }
                    }
                }
            },

            scales: {
                x: {
                    ticks: {
                        color: "#d0dced",
                        maxTicksLimit: 8
                    },

                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                },

                y: {
                    beginAtZero: true,

                    ticks: {
                        color: "#d0dced",
                        precision: isSubscribers ? 0 : undefined
                    },

                    grid: {
                        color: context =>
                            context.tick.value === 0
                                ? "rgba(255,255,255,0.55)"
                                : "rgba(255,255,255,0.1)"
                    }
                }
            }
        }
    });
}

async function loadAnalytics() {
    const message = document.getElementById(
        "chart-message"
    );

    try {
        const response = await fetch("/api/analytics");

        if (!response.ok) {
            throw new Error("Аналитика недоступна");
        }

        const data = await response.json();

        document.getElementById("views-28").textContent =
            formatNumber(data.views_28);

        document.getElementById("watch-time").textContent =
            formatNumber(data.watch_hours_28) + " ч";

        if (!Array.isArray(data.daily) || !data.daily.length) {
            message.textContent = "Нет данных за этот период";
            return;
        }

        analyticsData = data;

        message.textContent =
            "Последний день с данными: " +
            data.last_data_date;

        showChart("views");

        document.querySelectorAll(".chart-tab").forEach(
            button => {
                button.addEventListener("click", () => {
                    showChart(button.dataset.chart);
                });
            }
        );

    } catch (error) {
        console.error(error);
        message.textContent =
            "Не удалось загрузить аналитику";
    }
}

document.addEventListener(
    "DOMContentLoaded",
    loadAnalytics
);

