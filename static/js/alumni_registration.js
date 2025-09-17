// Alumni Registration Page JS (extracted from template)
// Requires: jQuery 3.6+, Select2 4.x

(function () {
    'use strict';

    // ---------- helpers ----------
    function $(sel) { return document.querySelector(sel); }
    function $all(sel) { return document.querySelectorAll(sel); }

    function showError(field, message) {
        if (!field) return;
        field.classList.add('border-red-500');
        let err = field.nextElementSibling;
        if (!err || !err.classList.contains('error-message')) {
            err = document.createElement('p');
            err.className = 'error-message text-red-500 text-sm mt-1';
            err.textContent = message;
            field.parentNode.insertBefore(err, field.nextSibling);
        }
        return err;
    }

    function clearError(field) {
        if (!field) return;
        field.classList.remove('border-red-500');
        const err = field.nextElementSibling;
        if (err && err.classList.contains('error-message')) err.remove();
    }

    function checkPasswordStrength(pwd) {
        const strong = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
        const medium = /^(?:(?=.*[a-z])(?=.*[A-Z])|(?=.*[A-Z])(?=.*\d)|(?=.*[a-z])(?=.*\d)).{6,}$/;
        if (strong.test(pwd)) return 'strong';
        if (medium.test(pwd)) return 'medium';
        return 'weak';
    }

    // ---------- DOM ready ----------
    document.addEventListener('DOMContentLoaded', function () {
        const form = $('form');
        if (!form) return;

        // No need for slider initialization as we're using checkboxes now

        // IDs (Django auto-generates "id_" + fieldname)
        const ids = {
            password1: 'id_password1',
            password2: 'id_password2',
            email: 'id_email',
            confirmEmail: 'id_confirm_email',
            dateOfBirth: 'id_date_of_birth',
            graduationYear: 'id_graduation_year',
            country: 'id_country',
            city: 'id_city',
            phone: 'id_mobile_number'
        };

        // ----- Select2 for country (Basic usage like the doc) -----
        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2) {
            const $ = window.jQuery;
            // Basic init on class; add fallbacks
            const $targets = $('.js-example-basic-single, #country, #' + ids.country);
            if ($targets.length) {
                $targets.select2();
                // Restore selected value when provided via data-selected
                $targets.each(function () {
                    const val = $(this).data('selected');
                    if (val) $(this).val(val).trigger('change');
                });
            }
        }

        // ----- Password strength -----
        const pwdInput = $('#' + ids.password1);
        const pwdMeter = $('#password-strength-meter');
        const pwdText = $('#password-strength-text');
        if (pwdInput) {
            pwdInput.addEventListener('input', function () {
                const val = this.value;
                const strength = checkPasswordStrength(val);
                if (!pwdMeter) return;
                const clsBase = 'w-full h-1.5 rounded ';
                if (strength === 'strong') {
                    pwdMeter.className = clsBase + 'bg-green-500';
                    if (pwdText) pwdText.textContent = 'Strong';
                } else if (strength === 'medium') {
                    pwdMeter.className = clsBase + 'bg-yellow-500';
                    if (pwdText) pwdText.textContent = 'Moderate';
                } else {
                    pwdMeter.className = clsBase + 'bg-red-500';
                    if (pwdText) pwdText.textContent = 'Weak';
                }
            });
        }

        // ----- Phone input with intl-tel-input -----
        const phoneInput = $('#' + ids.phone);
        let iti = null;
        if (phoneInput && window.intlTelInput) {
            iti = window.intlTelInput(phoneInput, {
                separateDialCode: true,
                utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/utils.js'
            });
            phoneInput.addEventListener('input', () => clearError(phoneInput));
        }

        // ----- Age validation -----
        const dobInput = $('#' + ids.dateOfBirth);
        function validateAge() {
            if (!dobInput || !dobInput.value) return true;
            const dob = new Date(dobInput.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const m = today.getMonth() - dob.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
            if (age < 18) {
                showError(dobInput, 'You must be at least 18 years old');
                return false;
            }
            clearError(dobInput);
            return true;
        }
        if (dobInput) {
            dobInput.addEventListener('blur', validateAge);
        }

        // ----- Email & password confirmation helpers -----
        const emailInput = $('#' + ids.email);
        const confirmEmail = $('#' + ids.confirmEmail);
        const confirmPwd = $('#' + ids.password2);

        function emailsMatch() {
            if (!emailInput || !confirmEmail) return true;
            if (emailInput.value !== confirmEmail.value) {
                showError(confirmEmail, 'Email addresses do not match');
                return false;
            }
            clearError(confirmEmail);
            return true;
        }

        function passwordsMatch() {
            if (!pwdInput || !confirmPwd) return true;
            if (pwdInput.value !== confirmPwd.value) {
                showError(confirmPwd, 'Passwords do not match');
                return false;
            }
            clearError(confirmPwd);
            return true;
        }

        if (emailInput && confirmEmail) {
            emailInput.addEventListener('input', emailsMatch);
            confirmEmail.addEventListener('input', emailsMatch);
        }
        if (pwdInput && confirmPwd) {
            pwdInput.addEventListener('input', passwordsMatch);
            confirmPwd.addEventListener('input', passwordsMatch);
        }

        // ----- Form submit validation -----
        form.addEventListener('submit', function (e) {
            let valid = true;

            // required fields
            $all('[required]').forEach(function (fld) {
                if (!fld.value.trim()) {
                    showError(fld, 'This field is required');
                    valid = false;
                }
            });

            // phone
            if (iti) {
                if (!iti.isValidNumber()) {
                    showError(phoneInput, 'Enter a valid phone number');
                    valid = false;
                } else {
                    phoneInput.value = iti.getNumber();
                }
            }

            if (dialSelect && phoneInput) {
                const combined = dialSelect.value + phoneInput.value.replace(/[^0-9]/g, '');
                if (!/^\+\d{6,15}$/.test(combined)) {
                    showError(phoneInput, 'Enter a valid phone number');
                    valid = false;
                } else {
                    phoneInput.value = combined; // write back full int-l number
                }
            }

            if (!validateAge()) valid = false;
            if (!emailsMatch()) valid = false;
            if (!passwordsMatch()) valid = false;

            if (!valid) {
                e.preventDefault();
                // scroll to first error
                const errEl = $('.error-message');
                if (errEl) errEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    });
})();
