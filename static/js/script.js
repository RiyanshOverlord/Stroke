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
    }, 2000); // 3 seconds timer
  }

  function isValidUsername(username) {
    return /^[a-zA-Z0-9_]+$/
      .test(username); // Returns false if username looks like an email
  }
  // Handle Login
  document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementsByName("login-email")[0].value;
    const password = document.getElementsByName("login-password")[0].value;

    try {
      const response = await fetch("/user_login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          form_type: "login",
          email: email,
          password: password,
        }),
      });

      const result = await response.json();
      console.log(response.ok)
      if (response.ok) {
        // alert(result.message);
        showToast(result.message, "success")

        setTimeout(() => { window.location.href = "/chatbot" }, 3000);
      } else {
        // alert(result.message);
        showToast(result.message, "error")
      }
    } catch (error) {
      console.error("Login Error:", error);
      alert("An error occurred during login. Please try again.");
    }
  });

  // Handle Registration
  document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementsByName("username")[0].value;
    const email = document.getElementsByName("register-email")[0].value;
    const password = document.getElementsByName("register-password")[0].value;

    if (isValidUsername(username)) {


      try {
        const response = await fetch("/user_login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            form_type: "register",
            username: username,
            email: email,
            password: password,
          }),
        });

        const result = await response.json();
        if (response.ok) {
          // alert(result.message);
          showToast(result.message, "success");
          document.getElementById("registerForm").reset();
          wrapper.classList.remove('active');


        } else {
          // alert(result.message);
          showToast(result.message, "success");
        }
      } catch (error) {
        console.error("Registration Error:", error);
        alert("An error occurred during registration. Please try again.");
      }
    } else {
      showToast("Invalid username format.", "error");
      return;
    }
  });

  registerLink.addEventListener('click', () => {
    wrapper.classList.add('active');
  })

  loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
  })

  btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
  })

  iconClose.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
  })

})
