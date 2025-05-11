document.addEventListener("DOMContentLoaded", () => {
  const headerUsernameEl = document.getElementById("headerUsername");
  const logoutButtonEl = document.getElementById("logoutButton");
  const loginLinkHeaderEl = document.getElementById("loginLinkHeader");

  // Предполагаем, что getCookie есть в authUtils.js
  const token =
    typeof getCookie === "function" ? getCookie("kurabye_access_token") : null;

  function decodeJwtTokenForHeader(token) {
    // немного дублируется, можно вынести в authUtils
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map(function (c) {
            return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join(""),
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  }

  if (token) {
    const decodedToken = decodeJwtTokenForHeader(token);
    const username = decodedToken
      ? decodedToken.user_name
      : localStorage.getItem("kurabye_user_name") || "Профиль";

    if (headerUsernameEl) {
      headerUsernameEl.textContent = username;
      headerUsernameEl.style.display = "inline";
      headerUsernameEl.href = "/profile.html"; // Сделаем имя ссылкой на профиль
    }
    if (logoutButtonEl) {
      logoutButtonEl.style.display = "inline-block";
      logoutButtonEl.addEventListener("click", () => {
        // Очищаем cookie и localStorage
        document.cookie =
          "kurabye_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax;";
        localStorage.removeItem("kurabye_user_name");
        window.location.href = "/"; // Редирект на главную
      });
    }
    if (loginLinkHeaderEl) {
      loginLinkHeaderEl.style.display = "none";
    }
  } else {
    if (headerUsernameEl) headerUsernameEl.style.display = "none";
    if (logoutButtonEl) logoutButtonEl.style.display = "none";
    if (loginLinkHeaderEl) {
      loginLinkHeaderEl.style.display = "inline-block";
      loginLinkHeaderEl.href = `/login.html?redirectUrl=${encodeURIComponent(window.location.pathname + window.location.search)}`;
    }
  }
});
