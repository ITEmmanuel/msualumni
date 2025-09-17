(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var phrases = [
      'Join MSU Alumni Network',
      'Connect with Fellow Alumni',
      'Stay Updated with MSU',
      'Be Part of Our Community'
    ];
    var ctaText = document.getElementById('cta-text');
    var arrow = document.querySelector('.arrow');
    var underline = document.querySelector('.underline');
    var phraseIndex = 0;
    var isDeleting = false;
    var typingSpeed = 120; // ms
    var pauseTime = 3000; // ms

    if (!ctaText) return;

    function typeWriter() {
      var currentPhrase = phrases[phraseIndex];
      if (isDeleting) {
        ctaText.textContent = currentPhrase.substring(0, ctaText.textContent.length - 1);
        typingSpeed = 80;
      } else {
        ctaText.textContent = currentPhrase.substring(0, ctaText.textContent.length + 1);
        typingSpeed = 120;
      }

      var progress = ctaText.textContent.length / currentPhrase.length;
      if (underline) {
        underline.style.transform = 'scaleX(' + progress + ')';
      }

      if (!isDeleting && ctaText.textContent === currentPhrase) {
        typingSpeed = pauseTime;
        isDeleting = true;
        if (arrow) arrow.style.opacity = '1';
        if (underline) underline.style.transformOrigin = 'right';
      } else if (isDeleting && ctaText.textContent === '') {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        if (arrow) arrow.style.opacity = '0';
        if (underline) underline.style.transformOrigin = 'left';
      }

      setTimeout(typeWriter, typingSpeed);
    }

    setTimeout(typeWriter, 500);

    var ctaParent = ctaText.parentElement;
    if (ctaParent) {
      ctaParent.addEventListener('mouseenter', function () {
        ctaText.textContent = '';
        phraseIndex = 0;
        isDeleting = false;
        if (arrow) arrow.style.opacity = '0';
        if (underline) underline.style.transform = 'scaleX(0)';
        typeWriter();
      });
    }
  });
})();


