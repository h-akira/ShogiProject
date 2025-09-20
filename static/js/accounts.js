/**
 * Account Pages JavaScript Functionality
 * Provides enhanced UX for account management pages
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeAccountPages();
});

function initializeAccountPages() {
  // Initialize password strength checker
  initPasswordStrength();

  // Initialize password match validation
  initPasswordMatch();

  // Initialize form validation
  initFormValidation();

  // Initialize loading states
  initLoadingStates();

  // Initialize animations
  initAnimations();

  // Initialize accessibility features
  initAccessibility();
}

/**
 * Password Strength Checker
 */
function initPasswordStrength() {
  const newPasswordInput = document.getElementById('newPassword');
  const strengthIndicator = document.getElementById('passwordStrength');
  const strengthFill = document.getElementById('strengthFill');
  const strengthText = document.getElementById('strengthText');

  if (!newPasswordInput || !strengthIndicator) return;

  newPasswordInput.addEventListener('input', function() {
    const password = this.value;

    if (password.length === 0) {
      strengthIndicator.style.display = 'none';
      return;
    }

    strengthIndicator.style.display = 'block';

    const strength = calculatePasswordStrength(password);
    updateStrengthIndicator(strength, strengthFill, strengthText);
  });
}

function calculatePasswordStrength(password) {
  let score = 0;
  let feedback = [];

  // Length check
  if (password.length >= 8) {
    score += 20;
  } else {
    feedback.push('8文字以上');
  }

  if (password.length >= 12) {
    score += 10;
  }

  // Character variety checks
  if (/[a-z]/.test(password)) {
    score += 15;
  } else {
    feedback.push('小文字');
  }

  if (/[A-Z]/.test(password)) {
    score += 15;
  } else {
    feedback.push('大文字');
  }

  if (/[0-9]/.test(password)) {
    score += 15;
  } else {
    feedback.push('数字');
  }

  if (/[^a-zA-Z0-9]/.test(password)) {
    score += 15;
  } else {
    feedback.push('記号');
  }

  // Complexity bonus
  if (password.length >= 16 && score >= 70) {
    score += 10;
  }

  // Common patterns penalty
  if (/(.)\1{2,}/.test(password)) {
    score -= 10; // Repeated characters
  }

  if (/123|abc|qwerty|password/i.test(password)) {
    score -= 20; // Common sequences
  }

  score = Math.max(0, Math.min(100, score));

  return {
    score: score,
    level: getStrengthLevel(score),
    feedback: feedback
  };
}

function getStrengthLevel(score) {
  if (score < 30) return 'weak';
  if (score < 60) return 'fair';
  if (score < 80) return 'good';
  return 'strong';
}

function updateStrengthIndicator(strength, fillElement, textElement) {
  if (!fillElement || !textElement) return;

  const colors = {
    weak: '#ef4444',
    fair: '#f59e0b',
    good: '#10b981',
    strong: '#059669'
  };

  const labels = {
    weak: '弱い',
    fair: '普通',
    good: '良い',
    strong: '強い'
  };

  fillElement.style.width = `${strength.score}%`;
  fillElement.style.backgroundColor = colors[strength.level];

  let text = `${labels[strength.level]} (${strength.score}%)`;
  if (strength.feedback.length > 0) {
    text += ` - 不足: ${strength.feedback.join(', ')}`;
  }

  textElement.textContent = text;
  textElement.style.color = colors[strength.level];
}

/**
 * Password Match Validation
 */
function initPasswordMatch() {
  const newPasswordInput = document.getElementById('newPassword');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  const matchIndicator = document.getElementById('passwordMatch');

  if (!newPasswordInput || !confirmPasswordInput || !matchIndicator) return;

  function checkPasswordMatch() {
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (confirmPassword.length === 0) {
      matchIndicator.style.display = 'none';
      return;
    }

    matchIndicator.style.display = 'block';

    if (newPassword === confirmPassword) {
      matchIndicator.innerHTML = '<i data-lucide="check-circle" style="width: 14px; height: 14px; color: var(--success);"></i> <span style="color: var(--success);">パスワードが一致します</span>';
      confirmPasswordInput.classList.remove('error');
    } else {
      matchIndicator.innerHTML = '<i data-lucide="x-circle" style="width: 14px; height: 14px; color: var(--error);"></i> <span style="color: var(--error);">パスワードが一致しません</span>';
      confirmPasswordInput.classList.add('error');
    }

    // Re-initialize Lucide icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  newPasswordInput.addEventListener('input', checkPasswordMatch);
  confirmPasswordInput.addEventListener('input', checkPasswordMatch);
}

/**
 * Form Validation
 */
function initFormValidation() {
  const forms = document.querySelectorAll('.account-form');

  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!validateForm(this)) {
        e.preventDefault();
        return false;
      }
    });

    // Real-time validation
    const inputs = form.querySelectorAll('.form-input');
    inputs.forEach(input => {
      input.addEventListener('blur', function() {
        validateField(this);
      });

      input.addEventListener('input', function() {
        // Clear error state on input
        this.classList.remove('error');
        const errorElement = this.parentNode.querySelector('.form-error');
        if (errorElement && !errorElement.textContent.trim()) {
          errorElement.style.display = 'none';
        }
      });
    });
  });
}

function validateForm(form) {
  let isValid = true;
  const inputs = form.querySelectorAll('.form-input[required], .form-input[data-required="true"]');

  inputs.forEach(input => {
    if (!validateField(input)) {
      isValid = false;
    }
  });

  // Additional validation for password forms
  if (form.id === 'changePasswordForm' || form.id === 'resetPasswordForm') {
    const newPassword = form.querySelector('#newPassword');
    const confirmPassword = form.querySelector('#confirmPassword');

    if (newPassword && confirmPassword) {
      if (newPassword.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'パスワードが一致しません');
        isValid = false;
      }

      if (newPassword.value.length < 8) {
        showFieldError(newPassword, 'パスワードは8文字以上である必要があります');
        isValid = false;
      }
    }
  }

  return isValid;
}

function validateField(input) {
  const value = input.value.trim();
  let isValid = true;

  // Required validation
  if (input.hasAttribute('required') || input.dataset.required === 'true') {
    if (!value) {
      showFieldError(input, 'この項目は必須です');
      isValid = false;
    }
  }

  // Email validation
  if (input.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showFieldError(input, '有効なメールアドレスを入力してください');
      isValid = false;
    }
  }

  // Confirmation code validation
  if (input.id === 'confirmationCode' && value) {
    if (!/^\d{6}$/.test(value)) {
      showFieldError(input, '6桁の数字を入力してください');
      isValid = false;
    }
  }

  if (isValid) {
    clearFieldError(input);
  }

  return isValid;
}

function showFieldError(input, message) {
  input.classList.add('error');

  let errorElement = input.parentNode.querySelector('.form-error');
  if (!errorElement) {
    errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.innerHTML = '<i data-lucide="alert-circle" style="width: 14px; height: 14px;"></i> <span></span>';
    input.parentNode.appendChild(errorElement);
  }

  const errorText = errorElement.querySelector('span');
  if (errorText) {
    errorText.textContent = message;
  }

  errorElement.style.display = 'flex';

  // Re-initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function clearFieldError(input) {
  input.classList.remove('error');
  const errorElement = input.parentNode.querySelector('.form-error');
  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

/**
 * Loading States
 */
function initLoadingStates() {
  const forms = document.querySelectorAll('.account-form');

  forms.forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = this.querySelector('.form-submit');
      if (submitBtn) {
        setButtonLoading(submitBtn, true);
      }
    });
  });
}

function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.disabled = true;
    button.classList.add('loading');

    const originalText = button.innerHTML;
    button.dataset.originalText = originalText;

    button.innerHTML = '<i data-lucide="loader-2" class="btn-icon" style="animation: spin 1s linear infinite;"></i> 処理中...';
  } else {
    button.disabled = false;
    button.classList.remove('loading');

    if (button.dataset.originalText) {
      button.innerHTML = button.dataset.originalText;
    }
  }

  // Re-initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

/**
 * Animations
 */
function initAnimations() {
  // Fade in animation for elements
  const fadeElements = document.querySelectorAll('.fade-in');
  fadeElements.forEach((element, index) => {
    element.style.animationDelay = `${index * 0.1}s`;
  });

  // Slide up animation for cards
  const slideElements = document.querySelectorAll('.slide-up');
  slideElements.forEach((element, index) => {
    element.style.animationDelay = `${index * 0.15}s`;
  });

  // Progress steps animation
  const progressSteps = document.querySelectorAll('.progress-step');
  progressSteps.forEach((step, index) => {
    setTimeout(() => {
      step.style.opacity = '1';
      step.style.transform = 'translateY(0)';
    }, index * 100);
  });
}

/**
 * Accessibility Features
 */
function initAccessibility() {
  // Add ARIA labels to password strength indicator
  const passwordInput = document.getElementById('newPassword');
  const strengthIndicator = document.getElementById('passwordStrength');

  if (passwordInput && strengthIndicator) {
    passwordInput.setAttribute('aria-describedby', 'passwordStrength');
    strengthIndicator.setAttribute('aria-live', 'polite');
  }

  // Add keyboard navigation for sidebar links
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  sidebarLinks.forEach(link => {
    link.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.click();
      }
    });
  });

  // Add focus management for forms
  const firstInput = document.querySelector('.form-input');
  if (firstInput) {
    firstInput.focus();
  }
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// CSS for spinner animation
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .password-strength {
    margin-top: var(--space-sm);
    padding: var(--space-sm);
    background: var(--gray-50);
    border-radius: var(--radius-md);
    border: 1px solid var(--gray-200);
  }

  .strength-label {
    font-size: 0.75rem;
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    margin-bottom: var(--space-xs);
  }

  .strength-bar {
    height: 4px;
    background: var(--gray-200);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: var(--space-xs);
  }

  .strength-fill {
    height: 100%;
    transition: all var(--transition-fast);
    border-radius: 2px;
  }

  .strength-text {
    font-size: 0.75rem;
    font-weight: var(--font-weight-medium);
  }

  .password-match {
    display: flex;
    align-items: center;
    gap: var(--space-xs);
    font-size: 0.75rem;
    margin-top: var(--space-xs);
  }

  .progress-step {
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s ease-in-out;
  }
`;
document.head.appendChild(style);