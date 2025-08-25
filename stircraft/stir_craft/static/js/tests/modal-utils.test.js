/**
 * Tests for ModalUtils class
 * Tests modal functionality including show/hide, keyboard handling, and accessibility
 */

describe('ModalUtils', () => {
    let modalHTML;
    
    beforeEach(() => {
        // Create mock modal DOM structure
        modalHTML = `
            <div>
                <button id="trigger-btn" data-modal-trigger="testModal">Open Modal</button>
                
                <div id="testModal" class="modal" aria-hidden="true">
                    <div class="modal-content">
                        <h2>Test Modal</h2>
                        <button id="modal-close" data-modal-close="testModal">Close</button>
                        <button id="focusable-btn">Focusable Button</button>
                        <input type="text" id="modal-input" placeholder="Test input">
                    </div>
                </div>
                
                <div id="anotherModal" class="modal" aria-hidden="true">
                    <div class="modal-content">
                        <h2>Another Modal</h2>
                    </div>
                </div>
            </div>
        `;
        
        createTestDOM(modalHTML);
        
        // Mock focus method
        HTMLElement.prototype.focus = jest.fn();
        
        // Load the modal utils script
        require('../modal-utils.js');
    });
    
    describe('Modal Show/Hide Functionality', () => {
        test('should show modal by ID', () => {
            const modal = document.getElementById('testModal');
            
            const result = window.showModal('testModal');
            
            expect(result).toBe(true);
            expect(modal.classList.contains('show')).toBe(true);
            expect(modal.getAttribute('aria-hidden')).toBe('false');
            expect(document.body.style.overflow).toBe('hidden');
        });
        
        test('should hide modal by ID', () => {
            const modal = document.getElementById('testModal');
            
            // First show the modal
            window.showModal('testModal');
            expect(modal.classList.contains('show')).toBe(true);
            
            // Then hide it
            const result = window.hideModal('testModal');
            
            expect(result).toBe(true);
            expect(modal.classList.contains('show')).toBe(false);
            expect(modal.getAttribute('aria-hidden')).toBe('true');
            expect(document.body.style.overflow).toBe('');
        });
        
        test('should toggle modal visibility', () => {
            const modal = document.getElementById('testModal');
            
            // Toggle from hidden to shown
            let result = window.toggleModal('testModal');
            expect(result).toBe(true);
            expect(modal.classList.contains('show')).toBe(true);
            
            // Toggle from shown to hidden
            result = window.toggleModal('testModal');
            expect(result).toBe(true);
            expect(modal.classList.contains('show')).toBe(false);
        });
        
        test('should return false for non-existent modal', () => {
            const result = window.showModal('nonExistentModal');
            expect(result).toBe(false);
        });
        
        test('should log warning for non-existent modal', () => {
            global.console.warn = jest.fn();
            
            window.showModal('nonExistentModal');
            
            expect(global.console.warn).toHaveBeenCalledWith(
                'Modal with ID "nonExistentModal" not found'
            );
        });
    });
    
    describe('Focus Management', () => {
        test('should focus first focusable element when showing modal', () => {
            const modal = document.getElementById('testModal');
            const firstFocusable = modal.querySelector('button');
            
            window.showModal('testModal');
            
            expect(firstFocusable.focus).toHaveBeenCalled();
        });
        
        test('should handle modals with no focusable elements', () => {
            // Create a modal with no focusable elements
            const emptyModal = document.createElement('div');
            emptyModal.id = 'emptyModal';
            emptyModal.className = 'modal';
            emptyModal.innerHTML = '<div class="modal-content"><p>No focusable elements</p></div>';
            document.body.appendChild(emptyModal);
            
            // Should not throw error
            expect(() => {
                window.showModal('emptyModal');
            }).not.toThrow();
        });
        
        test('should return focus to trigger element when hiding modal', () => {
            const triggerBtn = document.getElementById('trigger-btn');
            const modal = document.getElementById('testModal');
            
            // Set trigger reference
            modal.dataset.triggeredBy = 'trigger-btn';
            
            window.hideModal('testModal');
            
            expect(triggerBtn.focus).toHaveBeenCalled();
        });
    });
    
    describe('Keyboard Handling', () => {
        test('should close modal on Escape key', () => {
            const modal = document.getElementById('testModal');
            
            // Show modal
            window.showModal('testModal');
            expect(modal.classList.contains('show')).toBe(true);
            
            // Press Escape key
            const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(escapeEvent);
            
            expect(modal.classList.contains('show')).toBe(false);
        });
        
        test('should not close modal on other keys', () => {
            const modal = document.getElementById('testModal');
            
            window.showModal('testModal');
            
            // Press other keys
            const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
            document.dispatchEvent(enterEvent);
            
            expect(modal.classList.contains('show')).toBe(true);
        });
        
        test('should only close visible modals on Escape', () => {
            const modal1 = document.getElementById('testModal');
            const modal2 = document.getElementById('anotherModal');
            
            // Show first modal
            window.showModal('testModal');
            
            // Press Escape - should close visible modal
            const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(escapeEvent);
            
            expect(modal1.classList.contains('show')).toBe(false);
            expect(modal2.classList.contains('show')).toBe(false);
        });
    });
    
    describe('Click Outside to Close', () => {
        test('should close modal when clicking on modal backdrop', () => {
            const modal = document.getElementById('testModal');
            modal.classList.add('show');
            
            // Simulate click on modal backdrop (the modal element itself)
            const clickEvent = new MouseEvent('click', { bubbles: true });
            Object.defineProperty(clickEvent, 'target', { value: modal });
            
            window.dispatchEvent(clickEvent);
            
            expect(modal.classList.contains('show')).toBe(false);
        });
        
        test('should not close modal when clicking inside modal content', () => {
            const modal = document.getElementById('testModal');
            const modalContent = modal.querySelector('.modal-content');
            modal.classList.add('show');
            
            // Simulate click inside modal content
            const clickEvent = new MouseEvent('click', { bubbles: true });
            Object.defineProperty(clickEvent, 'target', { value: modalContent });
            
            window.dispatchEvent(clickEvent);
            
            expect(modal.classList.contains('show')).toBe(true);
        });
    });
    
    describe('Event Triggers', () => {
        test('should open modal when clicking trigger element', () => {
            const triggerBtn = document.getElementById('trigger-btn');
            const modal = document.getElementById('testModal');
            
            simulateEvent(triggerBtn, 'click');
            
            expect(modal.classList.contains('show')).toBe(true);
        });
        
        test('should close modal when clicking close button', () => {
            const closeBtn = document.getElementById('modal-close');
            const modal = document.getElementById('testModal');
            
            // Show modal first
            modal.classList.add('show');
            
            simulateEvent(closeBtn, 'click');
            
            expect(modal.classList.contains('show')).toBe(false);
        });
        
        test('should prevent default action on trigger clicks', () => {
            const triggerBtn = document.getElementById('trigger-btn');
            
            const clickEvent = new MouseEvent('click', { bubbles: true });
            clickEvent.preventDefault = jest.fn();
            
            triggerBtn.dispatchEvent(clickEvent);
            
            expect(clickEvent.preventDefault).toHaveBeenCalled();
        });
    });
    
    describe('Custom Events', () => {
        test('should dispatch modal:shown event when showing modal', () => {
            const modal = document.getElementById('testModal');
            const eventHandler = jest.fn();
            
            modal.addEventListener('modal:shown', eventHandler);
            
            window.showModal('testModal');
            
            expect(eventHandler).toHaveBeenCalled();
            expect(eventHandler.mock.calls[0][0].detail.modalId).toBe('testModal');
        });
        
        test('should dispatch modal:hidden event when hiding modal', () => {
            const modal = document.getElementById('testModal');
            const eventHandler = jest.fn();
            
            modal.addEventListener('modal:hidden', eventHandler);
            
            window.showModal('testModal');
            window.hideModal('testModal');
            
            expect(eventHandler).toHaveBeenCalled();
            expect(eventHandler.mock.calls[0][0].detail.modalId).toBe('testModal');
        });
    });
    
    describe('Backward Compatibility', () => {
        test('should provide global showModal function', () => {
            expect(typeof window.showModal).toBe('function');
        });
        
        test('should provide global hideModal function', () => {
            expect(typeof window.hideModal).toBe('function');
        });
        
        test('should provide global toggleModal function', () => {
            expect(typeof window.toggleModal).toBe('function');
        });
        
        test('should work with existing onclick handlers', () => {
            const modal = document.getElementById('testModal');
            
            // Simulate onclick="showModal('testModal')"
            window.showModal('testModal');
            
            expect(modal.classList.contains('show')).toBe(true);
        });
    });
});
