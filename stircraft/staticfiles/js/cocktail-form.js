/**
 * StirCraft Cocktail Form JavaScript
 * 
 * Handles dynamic ingredient form management and new ingredient creation
 * for the cocktail creation/editing forms.
 * 
 * Features:
 * - Dynamic addition of ingredient forms
 * - Proper Django formset management
 * - New ingredient creation modal handling
 * - Form validation and error handling
 * 
 * Dependencies:
 * - Bootstrap 5.x (for modals and styling)
 * - Django formset management forms
 */

class CocktailForm {
    constructor() {
        console.log('CocktailForm constructor called');
        
        const totalFormsElement = document.getElementById('id_components-TOTAL_FORMS');
        const maxFormsElement = document.getElementById('id_components-MAX_NUM_FORMS');
        
        console.log('Total forms element:', totalFormsElement);
        console.log('Max forms element:', maxFormsElement);
        
        if (!totalFormsElement || !maxFormsElement) {
            console.error('Required formset management elements not found!');
            return;
        }
        
        this.formCount = parseInt(totalFormsElement.value);
        this.maxForms = parseInt(maxFormsElement.value);
        
        console.log('Form count:', this.formCount, 'Max forms:', this.maxForms);
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupIngredientDropdowns();
    }
    
    bindEvents() {
        // Handle new ingredient creation modal
        this.bindNewIngredientEvents();
        
        // Handle dynamic ingredient form addition
        const addBtn = document.getElementById('add-ingredient-btn');
        if (addBtn) {
            console.log('Add ingredient button found, binding click event');
            addBtn.addEventListener('click', () => {
                console.log('Add ingredient button clicked');
                this.addIngredientForm();
            });
        } else {
            console.log('Add ingredient button NOT found');
        }
        
        // Handle ingredient deletion tracking
        document.addEventListener('change', (e) => {
            if (e.target.name && e.target.name.includes('DELETE')) {
                this.updateAddButtonState();
            }
        });
    }
    
    bindNewIngredientEvents() {
        // Handle new ingredient selection in dropdowns
        document.querySelectorAll('select[name$="ingredient"]').forEach(select => {
            select.addEventListener('change', (e) => {
                if (e.target.value === 'new_ingredient') {
                    this.showNewIngredientModal(e.target);
                }
            });
        });
        
        // Handle saving new ingredient
        const saveButton = document.getElementById('save-new-ingredient');
        console.log('Save button found:', saveButton);
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                console.log('Save new ingredient button clicked!');
                this.saveNewIngredient();
            });
        } else {
            console.error('Save new ingredient button not found!');
        }
    }
    
    setupIngredientDropdowns() {
        // Set up existing ingredient dropdowns
        document.querySelectorAll('select[name$="ingredient"]').forEach(select => {
            this.bindIngredientDropdown(select);
        });
    }
    
    bindIngredientDropdown(select) {
        select.addEventListener('change', (e) => {
            if (e.target.value === 'new_ingredient') {
                this.showNewIngredientModal(e.target);
            }
        });
        
        // Add search functionality
        this.addIngredientSearch(select);
    }
    
    addIngredientSearch(select) {
        // Add a simple search input above the select
        const wrapper = select.parentElement;
        
        // Check if search input already exists
        if (wrapper.querySelector('.ingredient-search')) {
            return;
        }
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control ingredient-search mb-2';
        searchInput.placeholder = 'Search ingredients...';
        searchInput.style.fontSize = '0.9em';
        
        // Insert search input before the select
        wrapper.insertBefore(searchInput, select);
        
        // Add search functionality
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const options = select.querySelectorAll('option');
            
            options.forEach(option => {
                if (option.value === '' || option.value === 'new_ingredient') {
                    return; // Don't hide empty option or "create new" option
                }
                
                const text = option.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    }
    
    showNewIngredientModal(triggerSelect) {
        console.log('showNewIngredientModal called with:', triggerSelect);
        
        const modal = new bootstrap.Modal(document.getElementById('newIngredientModal'));
        console.log('Modal created:', modal);
        
        modal.show();
        
        // Store reference to the select that triggered this
        document.getElementById('newIngredientModal').dataset.targetSelect = triggerSelect.id;
        
        // Reset the select to empty for now
        triggerSelect.value = '';
        
        console.log('Modal should be visible now');
    }
    
    async saveNewIngredient() {
        console.log('saveNewIngredient function called!');
        
        const form = document.getElementById('quick-ingredient-form');
        if (!form) {
            console.error('Quick ingredient form not found!');
            alert('Form not found. Please try again.');
            return;
        }
        
        console.log('Form found:', form);
        const formData = new FormData(form);
        
        // Debug: Log form data
        console.log('Form data being sent:');
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }
        
        // Clear previous error states
        this.clearFormErrors();
        
        // Get CSRF token - try multiple sources
        let csrfToken = window.stirCraftConfig?.csrfToken;
        
        if (!csrfToken) {
            // Try to get from form
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
            }
        }
        
        if (!csrfToken) {
            // Try to get from cookie
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            if (cookieValue) {
                csrfToken = cookieValue;
            }
        }
        
        if (!csrfToken) {
            console.error('No CSRF token found!');
            alert('CSRF token not found. Please refresh the page and try again.');
            return;
        }
        
        // Ensure CSRF token is in the form data
        if (!formData.has('csrfmiddlewaretoken')) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }
        
        // Get ingredient add URL from configuration
        const ingredientAddUrl = window.stirCraftConfig?.ingredientAddUrl || '/ingredients/create/';
        
        console.log('Sending request to:', ingredientAddUrl);
        console.log('CSRF Token:', csrfToken);
        
        try {
            const response = await fetch(ingredientAddUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'  // Important: include session cookies
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            const responseText = await response.text();
            console.log('Raw response:', responseText);
            
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (parseError) {
                console.error('Failed to parse JSON:', parseError);
                console.error('Response was:', responseText);
                alert('Server returned an invalid response. Check console for details.');
                return;
            }
            
            if (data.success) {
                this.handleNewIngredientSuccess(data);
            } else {
                console.log('Server returned error:', data);
                console.log('Form errors:', data.errors);
                this.handleFormErrors(data.errors || {});
                
                // Show a more user-friendly error message
                let errorMessage = data.error || 'Please correct the form errors.';
                if (data.errors && Object.keys(data.errors).length > 0) {
                    // Extract specific error messages, especially for name field
                    if (data.errors.name) {
                        errorMessage = data.errors.name.join('\n');
                    } else {
                        const errorDetails = Object.entries(data.errors)
                            .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
                            .join('\n');
                        errorMessage = `Validation errors:\n${errorDetails}`;
                    }
                }
                
                // Show a more helpful dialog instead of basic alert
                this.showIngredientErrorDialog(errorMessage);
            }
        } catch (error) {
            console.error('Network error:', error);
            alert('Error creating ingredient. Please try again.');
        }
    }
    
    showIngredientErrorDialog(errorMessage) {
        // Show a more helpful error dialog
        const isNameError = errorMessage.includes('already exists');
        
        if (isNameError) {
            // For duplicate ingredient errors, show a more helpful message
            alert(`Ingredient Already Exists!\n\n${errorMessage}\n\nTip: Try searching for the ingredient in the dropdown above before creating a new one.`);
        } else {
            alert('Error creating ingredient: ' + errorMessage);
        }
    }
    
    clearFormErrors() {
        // Remove error classes and messages
        const form = document.getElementById('quick-ingredient-form');
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
        
        const errorDivs = form.querySelectorAll('.invalid-feedback');
        errorDivs.forEach(div => {
            div.textContent = '';
        });
    }
    
    handleFormErrors(errors) {
        // Display field-specific errors
        Object.keys(errors).forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            const errorDiv = document.getElementById(`${fieldName}-error`);
            
            if (field) {
                field.classList.add('is-invalid');
            }
            
            if (errorDiv) {
                errorDiv.textContent = errors[fieldName].join(', ');
            }
        });
    }
    
    handleNewIngredientSuccess(data) {
        // Add the new ingredient to all ingredient dropdowns
        const newOption = new Option(data.ingredient.name, data.ingredient.id);
        document.querySelectorAll('select[name$="ingredient"]').forEach(select => {
            // Find the right optgroup to add to
            const typeGroup = select.querySelector(`optgroup[label="${data.ingredient.type_display}"]`);
            if (typeGroup) {
                typeGroup.appendChild(newOption.cloneNode(true));
            }
        });
        
        // Set the ingredient in the select that triggered this modal
        const targetSelectId = document.getElementById('newIngredientModal').dataset.targetSelect;
        if (targetSelectId) {
            const targetSelect = document.getElementById(targetSelectId);
            targetSelect.value = data.ingredient.id;
        }
        
        // Hide modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('newIngredientModal'));
        modal.hide();
        document.getElementById('quick-ingredient-form').reset();
        
        this.showSuccessMessage(data.ingredient.name);
    }
    
    showSuccessMessage(ingredientName) {
        const form = document.getElementById('quick-ingredient-form');
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong>Success!</strong> "${ingredientName}" has been added to your ingredients.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        form.parentElement.insertBefore(alertDiv, form);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
    
    addIngredientForm() {
        if (this.formCount >= this.maxForms) {
            alert(`Maximum ${this.maxForms} ingredients allowed.`);
            return;
        }
        
        // Get the last form as a template
        const lastForm = document.querySelector('.ingredient-row:last-child');
        if (!lastForm) return;
        
        // Clone the form
        const newForm = this.cloneIngredientForm(lastForm);
        
        // Update form count and management
        this.formCount++;
        document.getElementById('ingredient-forms').appendChild(newForm);
        this.updateFormIndices();
        document.getElementById('id_components-TOTAL_FORMS').value = this.formCount;
        
        // Set up the new form
        this.setupNewForm(newForm);
        
        // Update button state
        this.updateAddButtonState();
    }
    
    cloneIngredientForm(templateForm) {
        const newForm = templateForm.cloneNode(true);
        
        // Clear all input values
        const inputs = newForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
            // Remove any error classes
            input.classList.remove('is-invalid');
        });
        
        // Clear any error messages
        const errorDivs = newForm.querySelectorAll('.text-danger');
        errorDivs.forEach(div => div.remove());
        
        return newForm;
    }
    
    setupNewForm(newForm) {
        // Add ingredient options to the new select
        const newSelect = newForm.querySelector('select[name$="ingredient"]');
        if (newSelect) {
            this.addIngredientOptions(newSelect);
            this.bindIngredientDropdown(newSelect);
            
            // Focus on the new ingredient select
            setTimeout(() => newSelect.focus(), 100);
        }
    }
    
    addIngredientOptions(select) {
        // Get options from the first ingredient select as a template
        const templateSelect = document.querySelector('select[name$="ingredient"]');
        if (templateSelect) {
            select.innerHTML = templateSelect.innerHTML;
        }
    }
    
    updateFormIndices() {
        const forms = document.querySelectorAll('.ingredient-row');
        forms.forEach((form, index) => {
            // Update all form field names and IDs
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.name) {
                    input.name = input.name.replace(/components-\d+/, `components-${index}`);
                }
                if (input.id) {
                    input.id = input.id.replace(/id_components-\d+/, `id_components-${index}`);
                }
            });
            
            // Update labels
            const labels = form.querySelectorAll('label');
            labels.forEach(label => {
                if (label.getAttribute('for')) {
                    label.setAttribute('for', label.getAttribute('for').replace(/id_components-\d+/, `id_components-${index}`));
                }
            });
            
            // Update form ID
            form.id = `ingredient-${index}`;
        });
    }
    
    updateAddButtonState() {
        const addBtn = document.getElementById('add-ingredient-btn');
        const visibleForms = document.querySelectorAll('.ingredient-row:not([style*="display: none"])').length;
        const checkedDeletes = document.querySelectorAll('input[name*="DELETE"]:checked').length;
        const effectiveForms = visibleForms - checkedDeletes;
        const remaining = this.maxForms - effectiveForms;
        
        if (effectiveForms >= this.maxForms) {
            addBtn.disabled = true;
            addBtn.innerHTML = `<i class="bi bi-check-circle me-2"></i>Maximum ingredients reached`;
        } else {
            addBtn.disabled = false;
            if (remaining <= 2) {
                addBtn.innerHTML = `<i class="bi bi-plus-circle me-2"></i>Add More Ingredients (${remaining} remaining)`;
            } else {
                addBtn.innerHTML = `<i class="bi bi-plus-circle me-2"></i>Add More Ingredients`;
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cocktail form JavaScript loaded');
    // Only initialize if we're on a page with the cocktail form
    if (document.getElementById('cocktail-form')) {
        console.log('Cocktail form found, initializing CocktailForm');
        new CocktailForm();
    } else {
        console.log('No cocktail form found on this page');
    }
});

// Export for testing (Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CocktailForm };
}
