(function () {
  if (!document || !document.addEventListener) return;
  function toggleMaiden() {
    var gender = document.getElementById('id_gender') || document.querySelector('[name="gender"]');
    var container = document.getElementById('maiden-name-container');
    if (!gender || !container) return;
    var v = gender.value;
    if (v === 'F') {
      container.style.display = 'block';
    } else {
      container.style.display = 'none';
    }
  }
  document.addEventListener('DOMContentLoaded', function () {
    var gender = document.getElementById('id_gender') || document.querySelector('[name="gender"]');
    if (gender) {
      gender.addEventListener('change', toggleMaiden);
    }
    // initial
    toggleMaiden();
  });
})();


