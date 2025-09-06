// Modern mobile menu functionality
document.addEventListener('DOMContentLoaded', () => {
  // Get mobile menu toggle button and menu
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (mobileMenuToggle && navLinks) {
    mobileMenuToggle.addEventListener('click', () => {
      // Toggle mobile menu visibility
      mobileMenuToggle.classList.toggle('active');
      navLinks.classList.toggle('mobile-open');
      
      // Toggle hamburger animation
      const hamburger = mobileMenuToggle.querySelector('.hamburger');
      if (hamburger) {
        hamburger.classList.toggle('active');
      }
      
      // Prevent body scroll when mobile menu is open
      document.body.classList.toggle('mobile-menu-open');
    });
    
    // Close mobile menu when clicking on a link
    const navLinkItems = navLinks.querySelectorAll('a');
    navLinkItems.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenuToggle.classList.remove('active');
        navLinks.classList.remove('mobile-open');
        document.body.classList.remove('mobile-menu-open');
        
        const hamburger = mobileMenuToggle.querySelector('.hamburger');
        if (hamburger) {
          hamburger.classList.remove('active');
        }
      });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenuToggle.contains(e.target) && !navLinks.contains(e.target)) {
        mobileMenuToggle.classList.remove('active');
        navLinks.classList.remove('mobile-open');
        document.body.classList.remove('mobile-menu-open');
        
        const hamburger = mobileMenuToggle.querySelector('.hamburger');
        if (hamburger) {
          hamburger.classList.remove('active');
        }
      }
    });
  }
});
