// Initialize Lucide icons
document.addEventListener('DOMContentLoaded', function() {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});

// Form validation helpers
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;
  
  const inputs = form.querySelectorAll('input[required]');
  let isValid = true;
  
  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.classList.add('error');
      isValid = false;
    } else {
      input.classList.remove('error');
    }
  });
  
  return isValid;
}

// Password confirmation validation
function validatePasswordConfirmation(passwordId, confirmId) {
  const password = document.getElementById(passwordId);
  const confirm = document.getElementById(confirmId);
  
  if (password && confirm) {
    if (password.value !== confirm.value) {
      confirm.setCustomValidity('パスワードが一致しません');
      return false;
    } else {
      confirm.setCustomValidity('');
      return true;
    }
  }
  return true;
}