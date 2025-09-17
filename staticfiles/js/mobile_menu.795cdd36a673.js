(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('mobile-menu-button');
    var navLinks = document.getElementById('nav-links');
    if (!btn || !navLinks) return;
    btn.addEventListener('click', function () {
      if (navLinks.classList.contains('active')) navLinks.classList.remove('active');
      else navLinks.classList.add('active');
    });
  });
})();


