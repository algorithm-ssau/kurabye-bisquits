function getCookie(name) {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith(name + "=")) {
      return cookie.substring(name.length + 1);
    }
  }
  return null;
}

function decodeJwtTokenPayload(token) {
  if (!token) return null;
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
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
    console.error("Failed to decode JWT payload:", e);
    return null;
  }
}

function getUserIdFromJwt() {
  const token = getCookie("kurabye_access_token");
  if (!token) return null;
  const decoded = decodeJwtTokenPayload(token);
  return decoded ? decoded.user_id : null; // Предполагаем, что в JWT есть поле user_id
}

function checkAuthAndRedirect(loginPageUrl = "/login.html") {
  // Эта функция тоже должна быть
  const accessToken = getCookie("kurabye_access_token");
  if (!accessToken) {
    const currentPath =
      window.location.pathname + window.location.search + window.location.hash;
    window.location.href = `${loginPageUrl}?redirectUrl=${encodeURIComponent(currentPath)}`;
    return false;
  }
  return true;
}
