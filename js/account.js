document.addEventListener("DOMContentLoaded", checkAuth);

function checkAuth() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    redirectToLogin();
    return;
  }

  fetch("https://finalprogramacion3-backend-production.up.railway.app/auth/me", {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  })
    .then(res => {
      if (!res.ok) {
        throw new Error("Token inválido");
      }
      return res.json();
    })
    .then(user => {
    })
    .catch(() => {
      sessionStorage.removeItem("access_token");
      redirectToLogin();
    });
}

function redirectToLogin() {
  window.location.href = "login.html";
}