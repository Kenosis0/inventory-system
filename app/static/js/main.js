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
  const sidebar = document.querySelector('.sidebar');
  const scrim = document.querySelector('.sidebar-scrim');
  const menuTriggers = document.querySelectorAll('.mobile-menu-trigger');

  if (!sidebar || menuTriggers.length === 0) {
    return;
  }

  const setExpandedState = (isExpanded) => {
    menuTriggers.forEach((trigger) => {
      trigger.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    });
  };

  const closeSidebar = () => {
    sidebar.classList.remove('open');
    document.body.classList.remove('nav-open');
    setExpandedState(false);
  };

  const toggleSidebar = () => {
    if (window.innerWidth > 1024) {
      return;
    }

    const willOpen = !sidebar.classList.contains('open');
    sidebar.classList.toggle('open', willOpen);
    document.body.classList.toggle('nav-open', willOpen);
    setExpandedState(willOpen);
  };

  menuTriggers.forEach((trigger) => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleSidebar();
    });
  });

  if (scrim) {
    scrim.addEventListener('click', closeSidebar);
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeSidebar();
    }
  });

  sidebar.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 1024 && link.getAttribute('href') !== '#') {
        closeSidebar();
      }
    });
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) {
      closeSidebar();
    }
  });
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