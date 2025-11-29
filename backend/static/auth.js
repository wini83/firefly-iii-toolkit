async function login() {
    const username = document.getElementById("loginUser").value;
    const password = document.getElementById("loginPass").value;

    const response = await fetch("/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password })
    });

    if (!response.ok) {
        document.getElementById("loginError").innerText =
            "Nieprawidłowy login lub hasło";
        return;
    }

    const data = await response.json();

    localStorage.setItem("access_token", data.access_token);

    // redirect na dashboard / ostatni ekran
    window.location.href = "/upload";   // zdecydujesz jaki ma być landing page
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
}

// HTMX / Fetch: automatyczne dokładanie tokena
document.body.addEventListener("htmx:configRequest", evt => {
    const token = localStorage.getItem("access_token");
    if (token) evt.detail.headers["Authorization"] = "Bearer " + token;
});