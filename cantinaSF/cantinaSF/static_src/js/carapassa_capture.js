(function () {
  "use strict";

  function getCookie(name) {
    const item = document.cookie.split(";").map((value) => value.trim())
      .find((value) => value.startsWith(name + "="));
    return item ? item.slice(name.length + 1) : "";
  }

  document.addEventListener("DOMContentLoaded", async function () {
    const buttons = Array.from(document.querySelectorAll(".js-carapassa-capture"));
    if (!buttons.length) return;

    const bySubject = new Map(buttons.map((button) => [button.dataset.subjectId, button]));
    const popupsBySubject = new Map();

    async function refreshStatuses(subjectIds) {
      const response = await fetch(buttons[0].dataset.statusUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": decodeURIComponent(getCookie("csrftoken")),
        },
        body: JSON.stringify({ subject_ids: subjectIds }),
      });
      if (!response.ok) throw new Error("status request failed");
      const payload = await response.json();
      payload.subjects.forEach((subject) => {
        const button = bySubject.get(String(subject.subject_id));
        if (button) {
          button.dataset.faceRegistered = String(Boolean(subject.face_registered));
          button.textContent = subject.face_registered ? "Atualizar foto" : "Cadastrar foto";
          button.title = "";
        }
      });
    }

    try {
      await refreshStatuses(Array.from(bySubject.keys()));
    } catch (error) {
      buttons.forEach((button) => {
        button.textContent = "Cadastrar/Atualizar foto";
        button.title = "Não foi possível verificar se a foto já está cadastrada";
      });
    }

    buttons.forEach((button) => {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        const popup = window.open(
          button.href,
          "carapassa-capture-" + button.dataset.subjectId,
          "popup=yes,width=720,height=760,resizable=yes,scrollbars=yes"
        );
        if (popup) {
          const subjectId = button.dataset.subjectId;
          const wasRegistered = button.dataset.faceRegistered === "true";
          popupsBySubject.set(subjectId, popup);
          popup.focus();

          async function monitorCapture() {
            if (popup.closed) {
              popupsBySubject.delete(subjectId);
              try {
                await refreshStatuses([subjectId]);
              } catch (error) {
                button.textContent = "Cadastrar/Atualizar foto";
                button.title = "Não foi possível atualizar o status da foto";
              }
              return;
            }

            // A new enrollment can be detected even if CaraPassa does not close
            // the completion screen or send a postMessage notification.
            if (!wasRegistered) {
              try {
                await refreshStatuses([subjectId]);
                if (button.dataset.faceRegistered === "true") {
                  popup.close();
                  popupsBySubject.delete(subjectId);
                  return;
                }
              } catch (error) {
                // A transient failure must not interrupt capture monitoring.
              }
            }
            window.setTimeout(monitorCapture, 2000);
          }

          window.setTimeout(monitorCapture, 1000);
        } else {
          window.open(button.href, "_blank", "noopener");
        }
      });
    });

    window.addEventListener("message", function (event) {
      const allowedOrigins = new Set(buttons.map((button) => button.dataset.carapassaOrigin));
      if (!allowedOrigins.has(event.origin)) return;
      if (event.data?.type !== "carapassa.face_registered" || !event.data?.success) return;
      const subjectId = String(event.data.subject_id);
      const button = bySubject.get(subjectId);
      if (!button) return;

      button.textContent = "Atualizar foto";
      button.dataset.faceRegistered = "true";
      const popup = popupsBySubject.get(subjectId);
      if (popup && !popup.closed) popup.close();
      popupsBySubject.delete(subjectId);
    });
  });
})();
