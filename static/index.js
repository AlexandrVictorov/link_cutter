// сгенерировано с помощью GPT-5.2 для более наглядного тестирования сервиса и просто для красоты)
let isAuthorized = false;
let currentSlide = 0;
let regCaptchaId = null;

let statsDailyChartInstance = null;
let countryChartInstance = null;
let cityChartInstance = null;
let deviceChartInstance = null;

const slides = () => Array.from(document.querySelectorAll(".slide"));

document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    bindTabs();
    updateProtectedButtons();
    updateCarousel();
    loadRegisterCaptcha();
    initAdvancedAnalyticsDefaults();
});

async function loadRegisterCaptcha() {
    try {
        const response = await fetch("/captcha", { method: "GET" });
        const blob = await response.blob();
        regCaptchaId = response.headers.get("X-Captcha-Id");

        const url = URL.createObjectURL(blob);
        const img = document.getElementById("regCaptchaImage");
        if (img) img.src = url;
    } catch (e) {
        console.error("Ошибка загрузки капчи", e);
    }
}

function bindEvents() {
    document.getElementById("registerBtn").addEventListener("click", registerUser);
    document.getElementById("loginBtn").addEventListener("click", loginUser);
    document.getElementById("logoutBtn").addEventListener("click", logoutUser);

    document.getElementById("prevSlideBtn").addEventListener("click", prevSlide);
    document.getElementById("nextSlideBtn").addEventListener("click", nextSlide);

    document.getElementById("createBtn").addEventListener("click", createShortLink);
    document.getElementById("statsBtn").addEventListener("click", getStats);
    document.getElementById("advancedStatsBtn").addEventListener("click", getAdvancedStats);
    document.getElementById("searchBtn").addEventListener("click", searchLinks);
    document.getElementById("deleteBtn").addEventListener("click", deleteLink);
    document.getElementById("liveBtn").addEventListener("click", setLifetime);
    document.getElementById("setNBtn").addEventListener("click", setGlobalN);
    document.getElementById("replaceBtn").addEventListener("click", replaceShortCode);

    const forgotLink = document.getElementById("forgotPasswordLink");
    if (forgotLink) {
        forgotLink.addEventListener("click", (e) => {
            e.preventDefault();
            forgotPassword();
        });
    }

    const regReload = document.getElementById("regCaptchaReload");
    if (regReload) {
        regReload.addEventListener("click", (e) => {
            e.preventDefault();
            loadRegisterCaptcha();
        });
    }
}

function bindTabs() {
    const buttons = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(btn.dataset.tab).classList.add("active");
        });
    });
}

function setStatus(targetId, message, type = "info") {
    const el = document.getElementById(targetId);
    el.className = `status ${type}`;
    el.textContent = typeof message === "string" ? message : JSON.stringify(message, null, 2);
}

function normalizeErrorText(data) {
    if (!data) return "Неизвестная ошибка";
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return JSON.stringify(data.detail, null, 2);
    return JSON.stringify(data, null, 2);
}

async function safeJson(response) {
    const text = await response.text();
    if (!text) return null;
    try {
        return JSON.parse(text);
    } catch {
        return text;
    }
}

function setAuthState(state) {
    isAuthorized = state;
    const chip = document.getElementById("authChip");
    const appWrapper = document.getElementById("appWrapper");

    if (state) {
        chip.textContent = "🔐 Авторизован";
        chip.className = "auth-chip on";
        if (appWrapper) appWrapper.classList.remove("hidden");
    } else {
        chip.textContent = "🔓 Не авторизован";
        chip.className = "auth-chip off";
        if (appWrapper) appWrapper.classList.add("hidden");
    }

    updateProtectedButtons();
    updateCarousel();
}

function updateProtectedButtons() {
    document.querySelectorAll(".protected-btn").forEach(btn => {
        if (isAuthorized) {
            btn.classList.remove("btn-disabled");
            btn.disabled = false;
            if (btn.id === "deleteBtn") {
                btn.classList.add("btn-danger");
            } else {
                btn.classList.add("btn-primary");
            }
        } else {
            btn.classList.remove("btn-primary", "btn-danger");
            btn.classList.add("btn-disabled");
            btn.disabled = true;
        }
    });
}

function updateCarousel() {
    const allSlides = slides();
    allSlides.forEach((slide, index) => {
        slide.classList.toggle("active", index === currentSlide);
    });

    const active = allSlides[currentSlide];
    const title = active.dataset.title;
    const desc = active.dataset.desc;
    const method = active.dataset.method;
    const isPrivate = active.dataset.private === "true";

    document.getElementById("carouselTitle").textContent = title;
    document.getElementById("carouselDescription").textContent = desc;

    const methodPill = document.getElementById("methodPill");
    methodPill.textContent = method;
    methodPill.className = `pill ${method.toLowerCase()}`;

    const accessPill = document.getElementById("accessPill");
    accessPill.textContent = isPrivate ? "PRIVATE" : "PUBLIC";
    accessPill.className = `pill ${isPrivate ? "private" : "public"}`;

    const lockBadge = document.getElementById("lockBadge");
    if (isAuthorized) {
        lockBadge.textContent = "🔐 Доступно после входа";
        lockBadge.className = "lock-badge open";
    } else {
        lockBadge.textContent = "🔒 Авторизуйтесь";
        lockBadge.className = "lock-badge closed";
    }
}

function prevSlide() {
    const allSlides = slides();
    currentSlide = (currentSlide - 1 + allSlides.length) % allSlides.length;
    updateCarousel();
}

function nextSlide() {
    const allSlides = slides();
    currentSlide = (currentSlide + 1) % allSlides.length;
    updateCarousel();
}

function initAdvancedAnalyticsDefaults() {
    const dayInput = document.getElementById("advancedDay");
    if (dayInput && !dayInput.value) {
        dayInput.value = formatDateInput(new Date());
    }
}

function formatDateInput(date) {
    const year = date.getFullYear();
    const month = `${date.getMonth() + 1}`.padStart(2, "0");
    const day = `${date.getDate()}`.padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function formatDateTime(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("ru-RU");
}

function destroyChart(instance) {
    if (instance) instance.destroy();
    return null;
}

function normalizeChartItems(items, keyName) {
    if (!Array.isArray(items)) return [];
    return items.map(item => ({
        label: item?.[keyName] || "Unknown",
        value: Number(item?.clicks || 0)
    }));
}

function renderBarChart(canvasId, chartRefName, items, datasetLabel, color) {
    const normalized = normalizeChartItems(items, "label");
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (chartRefName === "country") countryChartInstance = destroyChart(countryChartInstance);
    if (chartRefName === "city") cityChartInstance = destroyChart(cityChartInstance);
    if (chartRefName === "device") deviceChartInstance = destroyChart(deviceChartInstance);

    const labels = normalized.map(item => item.label);
    const values = normalized.map(item => item.value);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: datasetLabel,
                data: values,
                backgroundColor: color,
                borderRadius: 8,
                maxBarThickness: 48
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });

    if (chartRefName === "country") countryChartInstance = chart;
    if (chartRefName === "city") cityChartInstance = chart;
    if (chartRefName === "device") deviceChartInstance = chart;
}

function renderDailyChart(items) {
    const canvas = document.getElementById("statsDailyChart");
    if (!canvas) return;

    statsDailyChartInstance = destroyChart(statsDailyChartInstance);

    const rows = Array.isArray(items) ? items : [];
    const labels = rows.map(item => item.date || item.day || "");
    const values = rows.map(item => Number(item.clicks || 0));

    statsDailyChartInstance = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Клики",
                data: values,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.12)",
                fill: true,
                tension: 0.28,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function renderReferrers(items) {
    const list = document.getElementById("referrersList");
    if (!list) return;

    list.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const li = document.createElement("li");
        li.className = "source-item";
        li.textContent = "Нет данных по источникам переходов за выбранный день.";
        list.appendChild(li);
        return;
    }

    items.forEach(item => {
        const li = document.createElement("li");
        li.className = "source-item";

        const name = document.createElement("span");
        name.className = "source-name";
        name.textContent = item.referrer || "Direct / None";

        const count = document.createElement("span");
        count.className = "source-count";
        count.textContent = `${Number(item.clicks || 0)} кликов`;

        li.appendChild(name);
        li.appendChild(count);
        list.appendChild(li);
    });
}

function renderStatsSummary(data) {
    const panel = document.getElementById("statsPanel");
    const created = document.getElementById("statsCreated");
    const clicks = document.getElementById("statsClicks");
    const lastClick = document.getElementById("statsLastClick");
    const originalUrl = document.getElementById("statsOriginalUrl");

    created.textContent = formatDateTime(data?.Created);
    clicks.textContent = Number(data?.Clicks ?? 0).toLocaleString("ru-RU");
    lastClick.textContent = formatDateTime(data?.Last_click);

    if (data?.Original_URL) {
        originalUrl.textContent = data.Original_URL;
        originalUrl.href = data.Original_URL;
    } else {
        originalUrl.textContent = "—";
        originalUrl.href = "#";
    }

    panel.classList.remove("hidden");
    renderDailyChart(data?.Clicks_by_day || []);
}

function renderAdvancedAnalytics(data) {
    const panel = document.getElementById("advancedPanel");
    panel.classList.remove("hidden");

    const byCountry = (data?.by_country || []).map(item => ({
        label: item.country || "Unknown",
        clicks: item.clicks || 0
    }));

    const byCity = (data?.by_city || []).map(item => ({
        label: item.city || "Unknown",
        clicks: item.clicks || 0
    }));

    const byDevice = (data?.by_device || []).map(item => ({
        label: item.device || "Unknown",
        clicks: item.clicks || 0
    }));

    renderBarChart("countryChart", "country", byCountry, "Клики по странам", "rgba(37, 99, 235, 0.72)");
    renderBarChart("cityChart", "city", byCity, "Клики по городам", "rgba(16, 185, 129, 0.72)");
    renderBarChart("deviceChart", "device", byDevice, "Клики по устройствам", "rgba(249, 115, 22, 0.72)");
    renderReferrers(data?.referrers || []);
}

async function registerUser() {
    const email = document.getElementById("regEmail").value.trim();
    const username = document.getElementById("regName").value.trim();
    const password = document.getElementById("regPassword").value.trim();
    const captcha_answer = document.getElementById("regCaptchaAnswer").value.trim();

    if (!email || !username || !password) {
        setStatus("authStatus", "Заполни имя, email и пароль.", "error");
        return;
    }

    if (!regCaptchaId || !captcha_answer) {
        setStatus("authStatus", "Заполни капчу.", "error");
        return;
    }

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email,
                password,
                username,
                captcha_id: regCaptchaId,
                captcha_answer
            })
        });

        const data = await safeJson(response);

        if (response.ok) {
            setStatus("authStatus", "Регистрация прошла успешно. Теперь перейди во вкладку 'Авторизация'.", "success");
            document.getElementById("loginEmail").value = email;
            document.getElementById("regCaptchaAnswer").value = "";
            loadRegisterCaptcha();
        } else {
            setStatus("authStatus", normalizeErrorText(data), "error");
            loadRegisterCaptcha();
        }
    } catch (e) {
        setStatus("authStatus", `Ошибка соединения: ${e.message}`, "error");
        loadRegisterCaptcha();
    }
}

async function loginUser() {
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    if (!email || !password) {
        setStatus("authStatus", "Заполни email и пароль для входа.", "error");
        return;
    }

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const response = await fetch("/auth/jwt/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
            credentials: "include"
        });

        const data = await safeJson(response);

        if (response.ok) {
            setAuthState(true);
            setStatus("authStatus", "Вход выполнен успешно.", "success");
        } else {
            setAuthState(false);
            setStatus("authStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setAuthState(false);
        setStatus("authStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function logoutUser() {
    try {
        const response = await fetch("/auth/jwt/logout", {
            method: "POST",
            credentials: "include"
        });

        if (response.ok) {
            setAuthState(false);
            setStatus("authStatus", "Выход выполнен.", "success");
        } else {
            const data = await safeJson(response);
            setStatus("authStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("authStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function forgotPassword() {
    const email = document.getElementById("loginEmail").value.trim();
    if (!email) {
        setStatus("authStatus", "Укажи email, на который зарегистрирован аккаунт.", "error");
        return;
    }

    try {
        const response = await fetch("/auth/forgot-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });

        if (response.ok) {
            setStatus(
                "authStatus",
                "Если такой email зарегистрирован, мы отправили письмо с ссылкой для смены пароля.",
                "success"
            );
        } else {
            const data = await safeJson(response);
            setStatus("authStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("authStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function createShortLink() {
    const original_url = document.getElementById("createOriginalUrl").value.trim();
    const alias = document.getElementById("createAlias").value.trim();
    const length = Number(document.getElementById("createLength").value);
    const expiresInput = document.getElementById("createExpiresAt").value;

    const card = document.getElementById("createdLinkCard");
    const anchor = document.getElementById("createdLinkAnchor");
    const copyBtn = document.getElementById("copyLinkBtn");

    card.classList.add("hidden");

    if (!original_url) {
        setStatus("apiStatus", "Укажи original_url.", "error");
        return;
    }

    const payload = { original_url, length };
    if (alias) payload.alias = alias;
    if (expiresInput) payload.expires_at = new Date(expiresInput).toISOString();

    try {
        const response = await fetch("/links/shorten", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            credentials: "include"
        });

        const data = await safeJson(response);

        if (response.ok) {
            const shortLink = data.short_link;
            anchor.href = shortLink;
            anchor.textContent = shortLink;
            card.classList.remove("hidden");

            copyBtn.onclick = async () => {
                try {
                    await navigator.clipboard.writeText(shortLink);
                    copyBtn.textContent = "Скопировано";
                    setTimeout(() => {
                        copyBtn.textContent = "Скопировать";
                    }, 1500);
                } catch {
                    copyBtn.textContent = "Не удалось скопировать";
                    setTimeout(() => {
                        copyBtn.textContent = "Скопировать";
                    }, 1500);
                }
            };

            setStatus("apiStatus", "Короткая ссылка успешно создана.", "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function getStats() {
    const shortCode = document.getElementById("statsShortCode").value.trim();
    if (!shortCode) {
        setStatus("apiStatus", "Укажи short_code.", "error");
        return;
    }

    try {
        const response = await fetch(`/links/${encodeURIComponent(shortCode)}/stats`, {
            method: "GET",
            credentials: "include"
        });

        const data = await safeJson(response);

        if (response.ok) {
            renderStatsSummary(data);
            setStatus("apiStatus", "Статистика по ссылке успешно загружена.", "success");
        } else {
            document.getElementById("statsPanel").classList.add("hidden");
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        document.getElementById("statsPanel").classList.add("hidden");
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function getAdvancedStats() {
    const shortCode = document.getElementById("advancedShortCode").value.trim();
    const day = document.getElementById("advancedDay").value;

    if (!shortCode) {
        setStatus("apiStatus", "Укажи short_code для расширенной аналитики.", "error");
        return;
    }

    if (!day) {
        setStatus("apiStatus", "Укажи день для расширенной аналитики.", "error");
        return;
    }

    try {
        const response = await fetch(`/links/${encodeURIComponent(shortCode)}/stats/regions?day=${encodeURIComponent(day)}`, {
            method: "GET",
            credentials: "include"
        });

        const data = await safeJson(response);

        if (response.ok) {
            renderAdvancedAnalytics(data);
            setStatus("apiStatus", "Расширенная аналитика за день успешно загружена.", "success");
        } else {
            document.getElementById("advancedPanel").classList.add("hidden");
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        document.getElementById("advancedPanel").classList.add("hidden");
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function searchLinks() {
    const originalUrl = document.getElementById("searchOriginalUrl").value.trim();
    if (!originalUrl) {
        setStatus("apiStatus", "Укажи original_url.", "error");
        return;
    }

    try {
        const response = await fetch(`/live/links/search?original_url=${encodeURIComponent(originalUrl)}`, {
            method: "GET",
            credentials: "include"
        });
        const data = await safeJson(response);
        if (response.ok) {
            setStatus("apiStatus", data, "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function deleteLink() {
    const shortCode = document.getElementById("deleteShortCode").value.trim();
    if (!shortCode) {
        setStatus("apiStatus", "Укажи short_code.", "error");
        return;
    }

    try {
        const response = await fetch(`/links/${encodeURIComponent(shortCode)}`, {
            method: "DELETE",
            credentials: "include"
        });
        const data = await safeJson(response);
        if (response.ok) {
            setStatus("apiStatus", data || "Ссылка удалена.", "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function setLifetime() {
    const alias = document.getElementById("liveAlias").value.trim();
    const expiresAt = document.getElementById("liveExpiresAt").value;

    if (!alias || !expiresAt) {
        setStatus("apiStatus", "Укажи alias и дату удаления.", "error");
        return;
    }

    try {
        const response = await fetch("/live/links/shorten", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                alias,
                expires_at: new Date(expiresAt).toISOString()
            }),
            credentials: "include"
        });
        const data = await safeJson(response);
        if (response.ok) {
            setStatus("apiStatus", data, "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function setGlobalN() {
    const n = document.getElementById("setNValue").value.trim();
    if (!n) {
        setStatus("apiStatus", "Укажи значение N.", "error");
        return;
    }

    try {
        const response = await fetch(`/live/links/shorten/set_n/${encodeURIComponent(n)}`, {
            method: "POST",
            credentials: "include"
        });
        const data = await safeJson(response);
        if (response.ok) {
            setStatus("apiStatus", data, "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}

async function replaceShortCode() {
    const shortCode = document.getElementById("replaceShortCode").value.trim();
    if (!shortCode) {
        setStatus("apiStatus", "Укажи текущий short_code.", "error");
        return;
    }

    try {
        const response = await fetch(`/links/${encodeURIComponent(shortCode)}`, {
            method: "PUT",
            credentials: "include"
        });
        const data = await safeJson(response);
        if (response.ok) {
            setStatus("apiStatus", data, "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("apiStatus", `Ошибка соединения: ${e.message}`, "error");
    }
}
