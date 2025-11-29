document.body.addEventListener("htmx:responseError", evt => {
    if (evt.detail.xhr.status === 401) {
        alert("Sesja wygasła. Zaloguj się ponownie.");
        localStorage.removeItem("access_token");
        window.location.href = "/login";
    }
});

async function loadPreview(fileId) {
    const container = document.getElementById("previewContainer");

    try {
        const r = await fetch(`/api/file/${fileId}`, {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            }
        });

        if (!r.ok) {
            container.innerHTML = `<div role="alert" class="alert alert-error">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        <span>Error! Task failed successfully.</span>
                                    </div>`;
            return;
        }

        const data = await r.json();
        const rows = data.content || [];

        container.innerHTML = renderPreviewTable(rows);

    } catch (e) {
        container.innerHTML = `<p class="text-red-600">Błąd połączenia</p>`;
    }
}

function renderPreviewTable(rows) {
    return `
        <div class="overflow-x-auto">
            <table class="table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Kwota</th>
                        <th>Szczegóły</th>
                        <th>Nadawca</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(r => `
                        <tr>
                            <td>${r.date ?? ""}</td>

                            <td class="${r.operation_amount < 0 ? "text-red-600" : "text-green-600"}">
                                ${r.amount ?? ""}${r.account_currency ?? ""}<br>
                                (${r.operation_amount ?? ""}${r.operation_currency ?? ""})
                            </td>

                            <td>
                                ${r.details ?? ""}<br>
                                ${r.recipient ?? ""}<br>
                                ${r.recipient_account ?? ""}
                            </td>

                            <td>
                                ${r.sender ?? ""}<br>
                                ${r.sender_account ?? ""}
                            </td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}
