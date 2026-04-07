const API = "";

let subgroups = [];
let submissions = [];
let activeTab = null;

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
    loadScoreboard();
    $("btn-request-pin").addEventListener("click", requestPin);
    $("btn-upload").addEventListener("click", uploadSubmission);
    $("btn-refresh").addEventListener("click", loadScoreboard);

    $("upload-toggle").addEventListener("click", () => {
        const body = $("upload-body");
        const toggle = $("upload-toggle");
        body.classList.toggle("collapsed");
        toggle.classList.toggle("open");
    });

    $("modal-close").addEventListener("click", closeVideoModal);
    $("video-modal").addEventListener("click", (e) => {
        if (e.target === $("video-modal")) closeVideoModal();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeVideoModal();
    });
});

async function requestPin() {
    const email = $("email").value.trim().toLowerCase();
    const status = $("email-status");

    if (!email.endsWith("@lpnu.ua")) {
        status.textContent = "Дозволені лише адреси @lpnu.ua";
        status.className = "status err";
        return;
    }

    $("btn-request-pin").disabled = true;
    status.textContent = "Надсилаємо...";
    status.className = "status";

    try {
        const resp = await fetch(`${API}/api/request-pin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
        });
        const data = await resp.json();
        if (resp.ok) {
            status.textContent = "PIN надіслано на вашу пошту!";
            status.className = "status ok";
            $("step-upload").classList.remove("hidden");
        } else {
            status.textContent = data.detail || "Помилка";
            status.className = "status err";
        }
    } catch (e) {
        status.textContent = "Помилка мережі";
        status.className = "status err";
    } finally {
        $("btn-request-pin").disabled = false;
    }
}

async function uploadSubmission() {
    const status = $("upload-status");
    const btn = $("btn-upload");

    const hpText = $("hyperparameters").value.trim();
    try {
        JSON.parse(hpText);
    } catch {
        status.textContent = "Гіперпараметри — невалідний JSON";
        status.className = "status err";
        return;
    }

    const formData = new FormData();
    formData.append("email", $("email").value.trim().toLowerCase());
    formData.append("pin", $("pin").value.trim());
    formData.append("name", $("name").value.trim());
    formData.append("surname", $("surname").value.trim());
    formData.append("subgroup", $("subgroup").value);
    formData.append("param_a", $("param_a").value);
    formData.append("hyperparameters", hpText);
    formData.append("model_standard", $("model_standard").files[0]);
    formData.append("model_individual", $("model_individual").files[0]);

    btn.disabled = true;
    status.textContent = "Завантажуємо...";
    status.className = "status";

    try {
        const resp = await fetch(`${API}/api/upload`, {
            method: "POST",
            body: formData,
        });
        const data = await resp.json();
        if (resp.ok) {
            status.textContent = "Модель завантажено! Оцінка розпочнеться автоматично.";
            status.className = "status ok";
            loadScoreboard();
        } else {
            status.textContent = data.detail || "Помилка завантаження";
            status.className = "status err";
        }
    } catch (e) {
        status.textContent = "Помилка мережі";
        status.className = "status err";
    } finally {
        btn.disabled = false;
    }
}

async function loadScoreboard() {
    try {
        const resp = await fetch(`${API}/api/scoreboard`);
        const data = await resp.json();
        subgroups = data.subgroups;
        submissions = data.submissions;
        populateSubgroupDropdown();
        renderTabs();
        renderTable();
    } catch (e) {
        $("scoreboard-content").innerHTML = "<p>Помилка завантаження рейтингу</p>";
    }
}

function populateSubgroupDropdown() {
    const sel = $("subgroup");
    sel.innerHTML = "";
    subgroups.forEach((sg) => {
        const opt = document.createElement("option");
        opt.value = sg;
        opt.textContent = sg;
        sel.appendChild(opt);
    });
}

function renderTabs() {
    const allGroups = new Set([...subgroups]);
    submissions.forEach((s) => allGroups.add(s.subgroup));

    const tabsEl = $("scoreboard-tabs");
    tabsEl.innerHTML = "";
    tabsEl.className = "tabs";

    const allTab = document.createElement("div");
    allTab.className = "tab" + (activeTab === null ? " active" : "");
    allTab.textContent = "Усі";
    allTab.addEventListener("click", () => { activeTab = null; renderTabs(); renderTable(); });
    tabsEl.appendChild(allTab);

    [...allGroups].sort().forEach((sg) => {
        const tab = document.createElement("div");
        tab.className = "tab" + (activeTab === sg ? " active" : "");
        tab.textContent = sg;
        tab.addEventListener("click", () => { activeTab = sg; renderTabs(); renderTable(); });
        tabsEl.appendChild(tab);
    });
}

function renderTable() {
    const filtered = activeTab
        ? submissions.filter((s) => s.subgroup === activeTab)
        : submissions;

    const sorted = [...filtered].sort((a, b) => (b.rank_score ?? -Infinity) - (a.rank_score ?? -Infinity));

    if (sorted.length === 0) {
        $("scoreboard-content").innerHTML = "<p>Немає результатів</p>";
        return;
    }

    let html = `<table>
        <thead><tr>
            <th>#</th>
            <th>Ім'я</th>
            <th>Підгрупа</th>
            <th>Стандарт</th>
            <th>Індивід.</th>
            <th>Рейтинг</th>
            <th>Статус</th>
            <th>Схожість</th>
            <th>Відео</th>
        </tr></thead><tbody>`;

    sorted.forEach((s, i) => {
        const rank = i + 1;
        const stdScore = formatScore(s.standard_mean);
        const indScore = formatScore(s.individual_mean);
        const rankScore = s.rank_score != null ? s.rank_score.toFixed(1) : "—";
        const statusBadge = `<span class="badge badge-${s.status}">${statusLabel(s.status)}</span>`;
        const dist = s.hyperparam_min_dist != null ? s.hyperparam_min_dist.toFixed(3) : "—";

        const videoCell = s.has_video
            ? `<td><button class="btn-video" onclick="openVideoModal(${s.id})">&#9654; Переглянути</button></td>`
            : `<td>—</td>`;

        html += `<tr>
            <td>${rank}</td>
            <td>${escHtml(s.name)} ${escHtml(s.surname)}</td>
            <td>${escHtml(s.subgroup)}</td>
            <td class="${scoreClass(s.standard_mean)}">${stdScore}</td>
            <td class="${scoreClass(s.individual_mean)}">${indScore}</td>
            <td><strong>${rankScore}</strong></td>
            <td>${statusBadge}</td>
            <td>${dist}</td>
            ${videoCell}
        </tr>`;
    });

    html += "</tbody></table>";
    $("scoreboard-content").innerHTML = html;
}

function formatScore(val) {
    if (val == null) return "—";
    return val.toFixed(1);
}

function scoreClass(val) {
    if (val == null) return "";
    if (val >= 200) return "score-good";
    if (val >= 0) return "score-mid";
    return "score-bad";
}

function statusLabel(status) {
    const labels = { pending: "Очікує", evaluating: "Оцінюється", done: "Готово", error: "Помилка" };
    return labels[status] || status;
}

function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function openVideoModal(subId) {
    const modal = $("video-modal");
    const video = $("modal-video");
    video.src = `/api/video/${subId}`;
    modal.classList.remove("hidden");
    video.play().catch(() => {});
}

function closeVideoModal() {
    const modal = $("video-modal");
    const video = $("modal-video");
    modal.classList.add("hidden");
    video.pause();
    video.src = "";
}
