document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector('input[name="birthday"]');
  if (!input) return;

  input.setAttribute('placeholder', 'dd/mm/aaaa');

  // Converte ISO (1988-05-06) para dd/mm/yyyy ao carregar a página
  if (/^\d{4}-\d{2}-\d{2}$/.test(input.value)) {
    const [year, month, day] = input.value.split("-");
    input.value = `${day}/${month}/${year}`;
  }

  // Aplica a máscara enquanto digita
  input.addEventListener("input", function (e) {
    let value = e.target.value.replace(/\D/g, "").slice(0, 8);
    if (value.length >= 5) {
      value = value.replace(/(\d{2})(\d{2})(\d{1,4})/, "$1/$2/$3");
    } else if (value.length >= 3) {
      value = value.replace(/(\d{2})(\d{1,2})/, "$1/$2");
    }
    e.target.value = value;
  });

  // Valida ao perder o foco
  input.addEventListener("blur", function (e) {
    const parts = e.target.value.split('/');
    if (parts.length === 3) {
      const [day, month, year] = parts;
      const isValid = day.length === 2 && month.length === 2 && year.length === 4 &&
                      !isNaN(Date.parse(`${year}-${month}-${day}`));
      if (!isValid) {
        e.target.value = '';
      } else {
        e.target.value = `${day}/${month}/${year}`;  // Garante o formato correto
      }
    } else {
      e.target.value = '';
    }
  });
});