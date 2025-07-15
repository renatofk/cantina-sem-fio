document.addEventListener("DOMContentLoaded", function () {
  const helpButtons = document.querySelectorAll('.sidebar-menu-item__link svg.icon-help');

  helpButtons.forEach((icon) => {
    const menuItem = icon.closest('.sidebar-menu-item');
    if (menuItem) {
      menuItem.style.display = 'none';
    }
  });
});