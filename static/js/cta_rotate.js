(function () {
  var phrases = [
    'Join MSU Alumni Network',
    'Connect with fellow alumni',
    'Unlock exclusive benefits',
    'Stay updated with MSU',
    'Grow your professional network',
    'Be part of our community'
  ];

  function rotateCTAText() {
    var ctaText = document.getElementById('cta-text');
    if (!ctaText) return;
    var currentIndex = 0;

    setTimeout(function rotate() {
      currentIndex = (currentIndex + 1) % phrases.length;
      ctaText.style.opacity = '0';

      setTimeout(function () {
        ctaText.textContent = phrases[currentIndex];
        ctaText.style.opacity = '1';
        var delay = currentIndex === 0 ? 2000 : 3000;
        setTimeout(rotate, delay);
      }, 300);
    }, 2000);
  }

  document.addEventListener('DOMContentLoaded', rotateCTAText);
})();


