// static/js/auth-form.js
document.addEventListener("DOMContentLoaded", () => {
  const loginFormEl = document.getElementById("loginForm");
  const registerFormEl = document.getElementById("registerForm");
  const loginErrorEl = document.getElementById("loginError");
  const registerErrorEl = document.getElementById("registerError");
  const registerSuccessEl = document.getElementById("registerSuccess");
  const tabButtons = document.querySelectorAll(".auth-tab-btn");

  const API_BASE_AUTH_URL = "/api/v1/auth"; // Base path for authentication API

  // Function to display messages (error or success)
  function showAuthMessage(element, messages, isError = true) {
    if (!element) return;
    element.innerHTML = ""; // Clear previous messages
    if (messages && messages.length > 0) {
      const ul = document.createElement("ul");
      messages.forEach((msgText) => {
        const li = document.createElement("li");
        li.textContent = msgText;
        ul.appendChild(li);
      });
      element.appendChild(ul);
      element.style.display = "block";
    } else {
      element.style.display = "none";
    }
    element.className = `form-message ${isError ? "error-message" : "success-message"}`;
  }

  // Function to decode JWT (simple client-side decoding for username)
  function decodeJwtPayload(token) {
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
      console.error("Could not decode JWT payload:", e);
      return null;
    }
  }

  // Tab switching logic
  if (tabButtons.length > 0 && loginFormEl && registerFormEl) {
    tabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        tabButtons.forEach((btn) => btn.classList.remove("active"));
        button.classList.add("active");

        const targetFormId = button.dataset.form; // 'login' or 'register'

        loginFormEl.classList.remove("active-form");
        registerFormEl.classList.remove("active-form");

        if (targetFormId === "login") {
          loginFormEl.classList.add("active-form");
        } else if (targetFormId === "register") {
          registerFormEl.classList.add("active-form");
        }

        // Clear messages when switching tabs
        if (loginErrorEl) loginErrorEl.style.display = "none";
        if (registerErrorEl) registerErrorEl.style.display = "none";
        if (registerSuccessEl) registerSuccessEl.style.display = "none";
      });
    });
  }

  // Login form submission
  if (loginFormEl) {
    loginFormEl.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitButton = loginFormEl.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Вход...";
      }
      if (loginErrorEl) loginErrorEl.style.display = "none";

      const formData = new FormData(loginFormEl);
      const params = new URLSearchParams();
      params.append("grant_type", "password"); // As per your cURL example
      params.append("username", formData.get("username"));
      params.append("password", formData.get("password"));
      // scope, client_id, client_secret are often optional for password grant
      // params.append('scope', formData.get('scope') || ''); // If you have these fields
      // params.append('client_id', formData.get('client_id') || '');
      // params.append('client_secret', formData.get('client_secret') || '');

      try {
        const response = await fetch(`${API_BASE_AUTH_URL}/token`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            accept: "application/json",
          },
          body: params.toString(),
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          console.log("Login successful:", data);
          const token = data.access_token;

          const expires = new Date(Date.now() + 3600 * 1000).toUTCString(); // 1 hour expiry
          document.cookie = `kurabye_access_token=${token}; path=/; expires=${expires}; SameSite=Lax; ${window.location.protocol === "https:" ? "Secure;" : ""}`;

          const decodedPayload = decodeJwtPayload(token);
          if (decodedPayload && decodedPayload.user_name) {
            localStorage.setItem("kurabye_user_name", decodedPayload.user_name);
          }

          // alert('Вход выполнен успешно!'); // You might not need this alert if redirecting immediately

          const urlParams = new URLSearchParams(window.location.search);
          const redirectUrl = urlParams.get("redirectUrl");
          window.location.href = redirectUrl ? redirectUrl : "/profile.html"; // Redirect to profile or intended page
        } else {
          let errorMessages = ["Неверное имя пользователя или пароль."];
          if (data.detail && typeof data.detail === "string") {
            errorMessages = [data.detail];
          } else if (
            data.detail &&
            Array.isArray(data.detail) &&
            data.detail[0] &&
            data.detail[0].msg
          ) {
            errorMessages = data.detail.map((err) => err.msg);
          } else if (data.message) {
            // Some APIs might return error in 'message'
            errorMessages = [data.message];
          }
          showAuthMessage(loginErrorEl, errorMessages);
        }
      } catch (error) {
        console.error("Login request error:", error);
        showAuthMessage(loginErrorEl, [
          "Произошла ошибка сети или сервера. Попробуйте снова.",
        ]);
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = "Войти";
        }
      }
    });
  }

  // Registration form submission
  if (registerFormEl) {
    registerFormEl.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitButton = registerFormEl.querySelector(
        'button[type="submit"]',
      );
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Регистрация...";
      }
      if (registerErrorEl) registerErrorEl.style.display = "none";
      if (registerSuccessEl) registerSuccessEl.style.display = "none";

      const usernameInput = registerFormEl.querySelector("#registerUsername");
      const passwordInput = registerFormEl.querySelector("#registerPassword");
      const passwordConfirmInput = registerFormEl.querySelector(
        "#registerPasswordConfirm",
      );

      const username = usernameInput ? usernameInput.value : "";
      const password = passwordInput ? passwordInput.value : "";
      const passwordConfirm = passwordConfirmInput
        ? passwordConfirmInput.value
        : "";

      if (password !== passwordConfirm) {
        showAuthMessage(registerErrorEl, ["Пароли не совпадают."]);
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = "Зарегистрироваться";
        }
        return;
      }

      const payload = {
        user_name: username,
        password: password,
      };

      try {
        const response = await fetch(`${API_BASE_AUTH_URL}/registration`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            accept: "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (response.ok) {
          console.log("Registration successful:", data);
          showAuthMessage(
            registerSuccessEl,
            ["Регистрация прошла успешно! Теперь вы можете войти."],
            false,
          );
          registerFormEl.reset();
          // Optionally, switch to login tab automatically
          // const loginTabButton = document.querySelector('.auth-tab-btn[data-form="login"]');
          // if (loginTabButton) loginTabButton.click();
        } else {
          let errorMessages = ["Ошибка при регистрации."];
          if (data.detail && Array.isArray(data.detail)) {
            errorMessages = data.detail.map((err) => {
              let fieldName = "Поле";
              if (err.loc && err.loc.length > 1) {
                if (err.loc[1] === "user_name") fieldName = "Имя пользователя";
                else if (err.loc[1] === "password") fieldName = "Пароль";
                else fieldName = err.loc[1];
              }
              let msg = err.msg
                .replace("Value error, ", "")
                .replace(
                  "String should have at least 8 characters",
                  "Пароль должен содержать минимум 8 символов",
                );
              return `${fieldName}: ${msg}`;
            });
          } else if (data.detail && typeof data.detail === "string") {
            errorMessages = [data.detail];
          } else if (data.error && data.error.message) {
            // Another possible error format
            errorMessages = [data.error.message];
          }
          showAuthMessage(registerErrorEl, errorMessages);
        }
      } catch (error) {
        console.error("Registration request error:", error);
        showAuthMessage(registerErrorEl, [
          "Произошла ошибка сети или сервера. Попробуйте снова.",
        ]);
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = "Зарегистрироваться";
        }
      }
    });
  }
});
