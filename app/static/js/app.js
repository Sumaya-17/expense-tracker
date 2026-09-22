document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("deleteModal");
  if (modal) modal.addEventListener("show.bs.modal", event => {
    const trigger = event.relatedTarget;
    document.getElementById("deleteForm").action = trigger.dataset.deleteUrl;
    document.getElementById("deleteMessage").textContent = `Delete “${trigger.dataset.itemName}”? This action cannot be undone.`;
  });
  document.querySelectorAll("form").forEach(form => form.addEventListener("submit", () => {
    const button = form.querySelector("button[type=submit], input[type=submit]");
    if (button && form.checkValidity()) { button.disabled = true; button.dataset.originalText = button.textContent; if (button.tagName === "BUTTON") button.textContent = "Saving…"; }
  }));
});
