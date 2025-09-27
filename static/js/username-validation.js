document.addEventListener('DOMContentLoaded', function() {
  const usernameField = document.querySelector('input[name="username"]');

  if (usernameField) {
    // Real-time validation
    usernameField.addEventListener('input', function() {
      const value = this.value;
      const isValid = /^[a-zA-Z0-9_-]*$/.test(value);

      // Remove existing error styling
      this.classList.remove('error');
      let existingError = this.parentNode.querySelector('.client-error');
      if (existingError) {
        existingError.remove();
      }

      // Add error if invalid characters found
      if (value && !isValid) {
        this.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error client-error';
        errorDiv.textContent = 'ユーザー名には半角英数字、アンダースコア(_)、ハイフン(-)のみ使用できます';
        this.parentNode.appendChild(errorDiv);
      }
    });

    // Form submission validation
    const form = usernameField.closest('form');
    if (form) {
      form.addEventListener('submit', function(e) {
        const value = usernameField.value;
        if (value && !/^[a-zA-Z0-9_-]+$/.test(value)) {
          e.preventDefault();
          usernameField.focus();

          // Show error if not already shown
          if (!usernameField.parentNode.querySelector('.client-error')) {
            usernameField.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error client-error';
            errorDiv.textContent = 'ユーザー名には半角英数字、アンダースコア(_)、ハイフン(-)のみ使用できます';
            usernameField.parentNode.appendChild(errorDiv);
          }
        }
      });
    }
  }
});