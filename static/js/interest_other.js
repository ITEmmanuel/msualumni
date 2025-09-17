(function () {
  if (!document || !document.addEventListener) return;
  function toggleOther() {
    var cb = document.getElementById('id_interest_other') || document.querySelector('[name="interest_other"]');
    var box = document.getElementById('interest-other-container');
    if (!cb || !box) return;
    if (cb.checked) {
      box.style.display = 'block';
    } else {
      box.style.display = 'none';
    }
  }
  document.addEventListener('DOMContentLoaded', function () {
    var cb = document.getElementById('id_interest_other') || document.querySelector('[name="interest_other"]');
    if (cb) cb.addEventListener('change', toggleOther);
    toggleOther();
  });
})();


