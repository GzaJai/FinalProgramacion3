document.addEventListener("DOMContentLoaded", checkAuth);

function checkAuth() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    redirectToLogin();
    return;
  }

  fetch("http://localhost:8000/auth/me", {
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
        if (user.role != "admin") {
            redirectToLogin();
        }
    })
    .catch(() => {
      sessionStorage.removeItem("access_token");
      redirectToLogin();
    });
}

function redirectToLogin() {
  window.location.href = "login.html";
}