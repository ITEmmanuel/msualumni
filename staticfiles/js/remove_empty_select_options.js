(function () {
  if (!document || !document.addEventListener) return;
  function cleanSelects() {
    var selects = document.querySelectorAll('select');
    for (var i = 0; i < selects.length; i++) {
      var sel = selects[i];
      // Remove leading empty/placeholder options ("", or "--------")
      while (sel.options.length && sel.options[0] && (sel.options[0].value === '' || sel.options[0].textContent.trim() === '--------')) {
        sel.remove(0);
      }
    }
  }
  document.addEventListener('DOMContentLoaded', cleanSelects);
})();


