(() => {
  const dialog = document.querySelector("#login-dialog");
  const loginForm = document.querySelector("#login-form");

  document.addEventListener("click", (event) => {
    const openButton = event.target.closest?.("[data-login-open]");
    if (!openButton || !dialog) return;

    event.preventDefault();
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    window.setTimeout(() => document.querySelector("#loginid")?.focus(), 0);
  });

  document.querySelectorAll("[data-login-close]").forEach((button) => {
    button.addEventListener("click", () => dialog?.close());
  });

  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.closest(".password-control")?.querySelector("input");
      if (!input) return;
      const showPassword = input.type === "password";
      input.type = showPassword ? "text" : "password";
      button.setAttribute("aria-label", showPassword ? "Hide password" : "Show password");
      button.innerHTML = `<i class="bi ${showPassword ? "bi-eye-slash" : "bi-eye"}"></i>`;
    });
  });

  document.querySelectorAll("[data-captcha-refresh]").forEach((button) => {
    button.addEventListener("click", async () => {
      const form = button.closest("form");
      const csrfToken = form?.querySelector('[name="csrfmiddlewaretoken"]')?.value;
      const question = form?.querySelector("[data-captcha-question]");
      if (!csrfToken || !question) return;

      button.disabled = true;
      try {
        const response = await fetch(button.dataset.captchaRefreshUrl || "/login/captcha", {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Could not refresh CAPTCHA");
        const data = await response.json();
        question.textContent = data.captcha_question;
        const answer = form.querySelector('[name="captcha_answer"]');
        if (answer) answer.value = "";
        form.querySelector("[data-login-feedback]").textContent = "";
      } catch {
        const feedback = form.querySelector("[data-login-feedback]");
        if (feedback) feedback.textContent = "Could not refresh the security check. Please try again.";
      } finally {
        button.disabled = false;
      }
    });
  });

  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = loginForm.querySelector('[type="submit"]');
      const feedback = loginForm.querySelector("[data-login-feedback]");
      const submitLabel = loginForm.querySelector("[data-submit-label]");
      const originalLabel = submitLabel?.textContent || "Sign in securely";
      submitButton.disabled = true;
      if (submitLabel) submitLabel.textContent = "Signing in…";
      if (feedback) feedback.textContent = "";

      try {
        const response = await fetch(loginForm.action, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
          },
          body: new FormData(loginForm),
        });
        const data = await response.json();
        if (data.ok) {
          window.location.assign(data.redirect_url);
          return;
        }
        if (feedback) feedback.textContent = data.error || "Unable to sign in. Please try again.";
        const question = loginForm.querySelector("[data-captcha-question]");
        const answer = loginForm.querySelector('[name="captcha_answer"]');
        if (question && data.captcha_question) question.textContent = data.captcha_question;
        if (answer) answer.value = "";
      } catch {
        if (feedback) feedback.textContent = "A network error occurred. Please try again.";
      } finally {
        submitButton.disabled = false;
        if (submitLabel) submitLabel.textContent = originalLabel;
      }
    });
  }
})();