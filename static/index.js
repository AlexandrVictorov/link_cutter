// сгенерировано с помощью GPT-5.2 для более наглядного тестирования сервиса и просто для красоты)
let isAuthorized = false;
let currentSlide = 0;

const slides = () => Array.from(document.querySelectorAll(".slide"));

document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    bindTabs();
    updateProtectedButtons();
    updateCarousel();
});

function bindEvents() {
    document.getElementById("registerBtn").addEventListener("click", registerUser);
    document.getElementById("loginBtn").addEventListener("click", loginUser);
    document.getElementById("logoutBtn").addEventListener("click", logoutUser);

    document.getElementById("prevSlideBtn").addEventListener("click", prevSlide);
    document.getElementById("nextSlideBtn").addEventListener("click", nextSlide);

    document.getElementById("createBtn").addEventListener("click", createShortLink);
    document.getElementById("statsBtn").addEventListener("click", getStats);
    document.getElementById("searchBtn").addEventListener("click", searchLinks);
    document.getElementById("deleteBtn").addEventListener("click", deleteLink);
    document.getElementById("liveBtn").addEventListener("click", setLifetime);
    document.getElementById("setNBtn").addEventListener("click", setGlobalN);
    document.getElementById("replaceBtn").addEventListener("click", replaceShortCode);
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
    if (state) {
        chip.textContent = "🔐 Авторизован";
        chip.className = "auth-chip on";
    } else {
        chip.textContent = "🔓 Не авторизован";
        chip.className = "auth-chip off";
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
    if (!isPrivate) {
        lockBadge.textContent = "🔓 Доступно без авторизации";
        lockBadge.className = "lock-badge open";
    } else if (isAuthorized) {
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

async function registerUser() {
    const email = document.getElementById("regEmail").value.trim();
    const username = document.getElementById("regName").value.trim();
    const password = document.getElementById("regPassword").value.trim();

    if (!email || !username || !password) {
        setStatus("authStatus", "Заполни имя, email и пароль.", "error");
        return;
    }

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, username })
        });

        const data = await safeJson(response);

        if (response.ok) {
            setStatus("authStatus", "Регистрация прошла успешно. Теперь перейди во вкладку 'Авторизация'.", "success");
            document.getElementById("loginEmail").value = email;
        } else {
            setStatus("authStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
        setStatus("authStatus", `Ошибка соединения: ${e.message}`, "error");
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
            setStatus("apiStatus", data, "success");
        } else {
            setStatus("apiStatus", normalizeErrorText(data), "error");
        }
    } catch (e) {
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
