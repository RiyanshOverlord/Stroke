document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.querySelector('.wrapper');
  const loginLink = document.querySelector('.login-link');
  const registerLink = document.querySelector('.register-link');
  const btnPopup = document.querySelector('.btnLogin-popup');
  const iconClose = document.querySelector('.icon-close');

  function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.className = "toast " + (type === "error" ? "error" : "");
    toast.innerHTML = message;
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
    }, 2000);
  }

  function isValidUsername(username) {
    return /^[a-zA-Z0-9_]+$/.test(username);
  }

  // Unified error-safe JSON parser
  async function safeParseJSON(response) {
    try {
      return await response.json();
    } catch (err) {
      console.error("Failed to parse JSON:", err);
      return { success: false, message: "Unexpected server response." };
    }
  }

  // Handle Login
  document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementsByName("login-email")[0].value;
    const password = document.getElementsByName("login-password")[0].value;

    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          form_type: "login",
          email: email,
          password: password,
        }),
      });

      const result = await safeParseJSON(response);
      if (response.ok && result.success) {
        showToast(result.message, "success");
        setTimeout(() => {
          window.location.href = "/chatbot";
        }, 2000);
      } else {
        showToast(result.message || "Login failed", "error");
      }
    } catch (error) {
      console.error("Login Error:", error);
      showToast("Server error during login.", "error");
    }
  });

  // Handle Registration
  document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementsByName("username")[0].value;
    const email = document.getElementsByName("register-email")[0].value;
    const password = document.getElementsByName("register-password")[0].value;

    if (!isValidUsername(username)) {
      showToast("Invalid username format.", "error");
      return;
    }

    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          form_type: "register",
          username: username,
          email: email,
          password: password,
        }),
      });

      const result = await safeParseJSON(response);
      if (response.ok && result.success) {
        showToast(result.message, "success");
        document.getElementById("registerForm").reset();
        wrapper.classList.remove('active');
      } else {
        showToast(result.message || "Registration failed", "error");
      }
    } catch (error) {
      console.error("Registration Error:", error);
      showToast("Server error during registration.", "error");
    }
  });

  // Form switches
  registerLink.addEventListener('click', () => {
    wrapper.classList.add('active');
  });

  loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
  });

  btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
  });

  iconClose.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
  });
});
