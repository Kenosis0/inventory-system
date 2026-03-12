// Inventory System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initFlashMessages();
  initSubmenu();
  initMobileNav();
});

// ===== FLASH MESSAGES =====
function initFlashMessages() {
  const closeButtons = document.querySelectorAll('.flash-close');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      this.parentElement.style.opacity = '0';
      setTimeout(() => {
        this.parentElement.remove();
      }, 300);
    });
  });
  
  // Auto-dismiss flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      setTimeout(() => {
        msg.remove();
      }, 300);
    }, 5000);
  });
}

// ===== SIDEBAR SUBMENU =====
function initSubmenu() {
  const submenuTriggers = document.querySelectorAll('.submenu-trigger > a');
  submenuTriggers.forEach(trigger => {
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      const parent = this.parentElement;
      parent.classList.toggle('active');
    });
  });
  
  // Keep submenu open if current page is within it
  const currentPath = window.location.pathname;
  document.querySelectorAll('.submenu a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.closest('.submenu-trigger').classList.add('active');
    }
  });
}

// ===== MOBILE NAVIGATION =====
function initMobileNav() {
  // Create mobile menu toggle button if needed
  if (window.innerWidth <= 1024) {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar && mainContent) {
      // Create toggle button
      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'mobile-nav-toggle';
      toggleBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      `;
      toggleBtn.style.cssText = `
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 101;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      `;
      toggleBtn.querySelector('svg').style.cssText = 'width: 24px; height: 24px;';
      
      document.body.appendChild(toggleBtn);
      
      // Toggle sidebar
      toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('open');
      });
      
      // Close sidebar when clicking outside
      document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      });
    }
  }
}

// ===== UTILITY FUNCTIONS =====

// Format number as currency
function formatCurrency(amount) {
  return '₱' + parseFloat(amount).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// Confirm delete action
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this item?');
}

// Debounce function for search inputs
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