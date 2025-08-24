/**
 * StirCraft Modal Utilities JavaScript
 * 
 * Provides reusable modal functionality across the application
 * 
 * Features:
 * - Show/hide modal functions
 * - Click-outside-to-close functionality
 * - Keyboard escape handling
 * - Focus management
 * 
 * Dependencies:
 * - Bootstrap 5.x (optional - can work with custom modals too)
 */

class ModalUtils {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindGlobalEvents();
        this.setupKeyboardHandling();
    }
    
    bindGlobalEvents() {
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                this.hideModal(event.target.id);
            }
        });
    }
    
    setupKeyboardHandling() {
        // Close modal on Escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                const visibleModal = document.querySelector('.modal.show');
                if (visibleModal) {
                    this.hideModal(visibleModal.id);
                }
            }
        });
    }
    
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal with ID "${modalId}" not found`);
            return false;
        }
        
        // Add show class for visibility
        modal.classList.add('show');
        
        // Set proper ARIA attributes
        modal.setAttribute('aria-hidden', 'false');
        
        // Focus management - focus first focusable element
        this.focusFirstElement(modal);
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Trigger custom event
        modal.dispatchEvent(new CustomEvent('modal:shown', { 
            detail: { modalId } 
        }));
        
        return true;
    }
    
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal with ID "${modalId}" not found`);
            return false;
        }
        
        // Remove show class
        modal.classList.remove('show');
        
        // Set proper ARIA attributes
        modal.setAttribute('aria-hidden', 'true');
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Return focus to trigger element if available
        this.returnFocus(modal);
        
        // Trigger custom event
        modal.dispatchEvent(new CustomEvent('modal:hidden', { 
            detail: { modalId } 
        }));
        
        return true;
    }
    
    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal with ID "${modalId}" not found`);
            return false;
        }
        
        if (modal.classList.contains('show')) {
            return this.hideModal(modalId);
        } else {
            return this.showModal(modalId);
        }
    }
    
    focusFirstElement(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    returnFocus(modal) {
        // Look for a stored trigger element
        const triggerId = modal.dataset.triggeredBy;
        if (triggerId) {
            const triggerElement = document.getElementById(triggerId);
            if (triggerElement) {
                triggerElement.focus();
            }
        }
    }
    
    // Store which element triggered the modal for focus return
    setTrigger(modalId, triggerElementId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.dataset.triggeredBy = triggerElementId;
        }
    }
}

// Create global instance
const modalUtils = new ModalUtils();

// Export functions for backward compatibility
window.showModal = function(modalId) {
    return modalUtils.showModal(modalId);
};

window.hideModal = function(modalId) {
    return modalUtils.hideModal(modalId);
};

window.toggleModal = function(modalId) {
    return modalUtils.toggleModal(modalId);
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up click handlers for modal triggers
    document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modalTrigger;
            modalUtils.setTrigger(modalId, trigger.id);
            modalUtils.showModal(modalId);
        });
    });
    
    // Set up click handlers for modal close buttons
    document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = closeBtn.dataset.modalClose || 
                           closeBtn.closest('.modal')?.id;
            if (modalId) {
                modalUtils.hideModal(modalId);
            }
        });
    });
});

// Export for testing (Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ModalUtils };
}
