
let analyticsChart = null;
let analyticsData = null;
let currentSubscribers = null;
let currentChart = "views";
let currentPeriod = "28";

function periodStart(endDate, period) {
    const end = new Date(endDate + "T00:00:00Z");
    if (period === "year") {
        const month = end.getUTCMonth();
        end.setUTCFullYear(end.getUTCFullYear() - 1);
        if (end.getUTCMonth() !== month) end.setUTCDate(0);
        end.setUTCDate(end.getUTCDate() + 1);
    } else {
        end.setUTCDate(end.getUTCDate() - 27);
    }
    return end.toISOString().slice(0, 10);
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    return Number(value).toLocaleString("ru-RU");
}


// Публичная статистика YouTube
async function loadStats() {
    try {
        const response = await fetch("/api/stats");

        if (!response.ok) {
            throw new Error("Ошибка загрузки статистики");
        }

        const data = await response.json();

        document.getElementById("subscribers").textContent =
            formatNumber(data.subscribers);

        document.getElementById("videos").textContent =
            formatNumber(data.videos);

        document.getElementById("total-views").textContent =
            formatNumber(data.total_views);

        if (
            data.subscribers !== null &&
            data.subscribers !== undefined
        ) {
            currentSubscribers = Number(data.subscribers);
        }
        if (analyticsData && currentChart === "subscribers") showChart(currentChart);

        console.log("Публичная статистика загружена");

    } catch (error) {
        console.error("Ошибка публичной статистики:", error);
    }
}


// Переключение графиков
function showChart(type) {
    currentChart = type;
    document.querySelectorAll(".chart-tab").forEach(button => {
        button.classList.toggle("active", button.dataset.chart === type);
        button.setAttribute("aria-pressed", String(button.dataset.chart === type));
    });
    if (!analyticsData || !analyticsData.daily?.length) {
        return;
    }

    const isSubscribers = type === "subscribers";
    const end = analyticsData.period_end || analyticsData.last_data_date;
    const start = periodStart(end, currentPeriod);
    const daily = analyticsData.daily.filter(item => item.date >= start && item.date <= end);
    const message = document.getElementById("chart-message");
    const canvas = document.getElementById("viewsChart");
    if (analyticsChart) {
        analyticsChart.destroy();
        analyticsChart = null;
    }
    canvas.hidden = true;
    document.getElementById("chart-title").textContent = isSubscribers
        ? "История подписчиков" : "Путешествие просмотров";
    if (!daily.length) {
        message.textContent = "Нет данных за этот период";
        return;
    }

    const labels = daily.map(item => item.date);

    let values;

    if (isSubscribers) {
        if (!Number.isFinite(currentSubscribers)) {
            document.getElementById("chart-message").textContent =
                "Не удалось получить количество подписчиков";
            return;
        }

        if (!daily.every(item =>
            Number.isFinite(Number(item.subscribers_net))
            && item.subscribers_net !== undefined
            && item.subscribers_net !== null
        )) {
            document.getElementById("chart-message").textContent =
                "Обнови analytics.json: нет истории подписчиков";
            return;
        }

        const totalNet = daily.reduce(
            (sum, item) => sum + Number(item.subscribers_net),
            0
        );

        let subscribers = currentSubscribers - totalNet;

        values = daily.map(item => {
            subscribers += Number(item.subscribers_net);
            return subscribers;
        });

    } else {
        values = daily.map(item => Number(item.views));
    }

    const color = isSubscribers
        ? "#38f5e0"
        : "#ffd36e";

    const fillColor = isSubscribers
        ? "rgba(56,245,224,0.14)"
        : "rgba(255,211,110,0.14)";

    document.getElementById("chart-title").textContent =
        isSubscribers
            ? "История подписчиков"
            : "Путешествие просмотров";

    document.querySelectorAll(".chart-tab").forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.chart === type
        );
    });

    if (analyticsChart) {
        analyticsChart.destroy();
    }

    canvas.hidden = false;

    analyticsChart = new Chart(canvas, {
        type: "line",

        data: {
            labels: labels,

            datasets: [{
                label: isSubscribers
                    ? "Всего подписчиков"
                    : "Просмотры",

                data: values,

                borderColor: color,
                backgroundColor: fillColor,

                borderWidth: 3,
                pointRadius: currentPeriod === "year" ? 0 : 4,
                pointHoverRadius: 7,

                pointBackgroundColor: color,
                pointBorderColor: "#ffffff",
                pointBorderWidth: 1,

                tension: 0.3,
                fill: true
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

                            return isSubscribers
                                ? " Подписчиков: " +
                                    formatNumber(value)
                                : " Просмотры: " +
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
                    beginAtZero: !isSubscribers,

                    ticks: {
                        color: "#d0dced",
                        precision: isSubscribers ? 0 : undefined,

                        callback: value =>
                            formatNumber(value)
                    },

                    grid: {
                        color: "rgba(255,255,255,0.1)"
                    }
                }
            }
        }
    });

    document.getElementById("chart-message").textContent =
        "Последний день с данными: " +
        analyticsData.last_data_date +
        (isSubscribers
            ? " · История приблизительная"
            : "") +
        (analyticsData.period_start > start
            ? " · Доступны данные с " + analyticsData.period_start
            : "");
}


// Аналитика за 28 дней
async function loadAnalytics() {
    const message = document.getElementById("chart-message");

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

        showChart("views");

        document.querySelectorAll(".chart-tab").forEach(button => {
            button.addEventListener("click", () => {
                showChart(button.dataset.chart);
            });
        });
        document.querySelectorAll("[data-period]").forEach(button => {
            button.addEventListener("click", () => {
                currentPeriod = button.dataset.period;
                document.querySelectorAll("[data-period]").forEach(filter => {
                    const active = filter === button;
                    filter.classList.toggle("active", active);
                    filter.setAttribute("aria-pressed", String(active));
                });
                showChart(currentChart);
            });
        });

    } catch (error) {
        console.error("Ошибка аналитики:", error);
        message.textContent =
            "Не удалось загрузить аналитику";
    }
}


// Запуск после загрузки страницы
document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([
        loadStats(),
        loadAnalytics()
    ]);
});
