function getCookie(name) {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    // Does this cookie string begin with the name we want?
    if (cookie.startsWith(name + "=")) {
      return cookie.substring(name.length + 1);
    }
  }
  return null;
}

function checkAuthAndRedirect(loginPageUrl = "/login.html") {
  const accessToken = getCookie("kurabye_access_token");

  if (!accessToken) {
    console.warn("Access token not found. Redirecting to login page.");
    const currentPath =
      window.location.pathname + window.location.search + window.location.hash;
    window.location.href = `${loginPageUrl}?redirectUrl=${encodeURIComponent(currentPath)}`;
    return false;
  }
  return true;
}
