// Employment fields handler (CSP-safe, no eval, no inline strings)
(function () {
  if (!document || !document.addEventListener) return;

  function log() {
    if (window && window.console && console.log) {
      try { console.log.apply(console, arguments); } catch (_) {}
    }
  }

  function handleEmploymentChange(selectEl) {
    var value = selectEl && selectEl.value ? selectEl.value : '';
    log('[employment_fields] change detected:', value);
    var detailContainers = document.querySelectorAll('.employment-detail');
    var otherContainer = document.getElementById('employment-other-container');
    log('[employment_fields] detail containers found:', detailContainers.length, 'other container exists:', !!otherContainer);

    // Hide all
    for (var i = 0; i < detailContainers.length; i++) {
      detailContainers[i].style.display = 'none';
      detailContainers[i].style.visibility = 'hidden';
    }
    if (otherContainer) {
      otherContainer.style.display = 'none';
      otherContainer.style.visibility = 'hidden';
    }

    // Show based on value
    // Formally employed: show Name of Organisation + Designation + Industry; hide 'other'
    // Self employed: hide Name of Organisation; show Designation + Industry; show 'other' for description
    // Not yet employed (unemployed): hide Name of Organisation; show 'other' for description; hide Designation/Industry
    // Other: hide all 3 details; show 'other'
    if (value === 'formally_employed') {
      log('[employment_fields] formally employed');
      for (var j = 0; j < detailContainers.length; j++) {
        // Index mapping relies on DOM order: 0=org, 1=job, 2=industry
        if (j === 0 || j === 1 || j === 2) {
          detailContainers[j].style.display = 'block';
          detailContainers[j].style.visibility = 'visible';
        }
      }
      if (otherContainer) {
        otherContainer.style.display = 'none';
        otherContainer.style.visibility = 'hidden';
      }
    } else if (value === 'self_employed') {
      log('[employment_fields] self employed');
      for (var k = 0; k < detailContainers.length; k++) {
        // hide org (index 0), show job (1) and industry (2)
        if (k === 0) {
          detailContainers[k].style.display = 'none';
          detailContainers[k].style.visibility = 'hidden';
        } else if (k === 1 || k === 2) {
          detailContainers[k].style.display = 'block';
          detailContainers[k].style.visibility = 'visible';
        }
      }
      if (otherContainer) {
        otherContainer.style.display = 'block';
        otherContainer.style.visibility = 'visible';
      }
    } else if (value === 'unemployed') {
      log('[employment_fields] not yet employed');
      for (var m = 0; m < detailContainers.length; m++) {
        // hide all formal details (org, job, industry)
        detailContainers[m].style.display = 'none';
        detailContainers[m].style.visibility = 'hidden';
      }
      if (otherContainer) {
        otherContainer.style.display = 'block';
        otherContainer.style.visibility = 'visible';
      }
    } else if (value === 'other') {
      log('[employment_fields] other');
      for (var n = 0; n < detailContainers.length; n++) {
        detailContainers[n].style.display = 'none';
        detailContainers[n].style.visibility = 'hidden';
      }
      if (otherContainer) {
        otherContainer.style.display = 'block';
        otherContainer.style.visibility = 'visible';
      }
    }
  }

  function initEmploymentFields() {
    var selectById = document.getElementById('id_employment_status');
    var selectByName = selectById || document.querySelector('[name="employment_status"]');
    var selectAny = selectByName || document.querySelector('select[id*="employment"]');
    var selectEl = selectAny;

    if (!selectEl) {
      log('[employment_fields] employment select not found');
      return;
    }

    log('[employment_fields] select found with id/name:', selectEl.id || selectEl.name || '(no id/name)');
    selectEl.addEventListener('change', function () {
      handleEmploymentChange(selectEl);
    });
    log('[employment_fields] change listener attached');
    // Initial run
    handleEmploymentChange(selectEl);
    log('[employment_fields] initial run complete, current value:', selectEl.value);
  }

  document.addEventListener('DOMContentLoaded', function () {
    log('[employment_fields] DOMContentLoaded fired');
    try { initEmploymentFields(); } catch (e) { log('[employment_fields] init error', e); }
  });
})();
