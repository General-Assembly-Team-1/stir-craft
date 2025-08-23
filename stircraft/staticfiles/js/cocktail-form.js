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
        this.formCount = parseInt(document.getElementById('id_recipecomponent_set-TOTAL_FORMS').value);
        this.maxForms = parseInt(document.getElementById('id_recipecomponent_set-MAX_NUM_FORMS').value);
        
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
        document.getElementById('add-ingredient-btn').addEventListener('click', () => {
            this.addIngredientForm();
        });
        
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
        document.getElementById('save-new-ingredient').addEventListener('click', () => {
            this.saveNewIngredient();
        });
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
    }
    
    showNewIngredientModal(triggerSelect) {
        const modal = new bootstrap.Modal(document.getElementById('newIngredientModal'));
        modal.show();
        
        // Store reference to the select that triggered this
        document.getElementById('newIngredientModal').dataset.targetSelect = triggerSelect.id;
        
        // Reset the select to empty for now
        triggerSelect.value = '';
    }
    
    async saveNewIngredient() {
        const form = document.getElementById('quick-ingredient-form');
        const formData = new FormData(form);
        
        // Get CSRF token from configuration or DOM
        const csrfToken = window.stirCraftConfig?.csrfToken || 
                         document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Get ingredient add URL from configuration
        const ingredientAddUrl = window.stirCraftConfig?.ingredientAddUrl || '/ingredients/add/';
        
        try {
            const response = await fetch(ingredientAddUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.handleNewIngredientSuccess(data);
            } else {
                alert('Error creating ingredient: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating ingredient. Please try again.');
        }
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
        document.getElementById('id_recipecomponent_set-TOTAL_FORMS').value = this.formCount;
        
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
                    input.name = input.name.replace(/recipecomponent_set-\d+/, `recipecomponent_set-${index}`);
                }
                if (input.id) {
                    input.id = input.id.replace(/id_recipecomponent_set-\d+/, `id_recipecomponent_set-${index}`);
                }
            });
            
            // Update labels
            const labels = form.querySelectorAll('label');
            labels.forEach(label => {
                if (label.getAttribute('for')) {
                    label.setAttribute('for', label.getAttribute('for').replace(/id_recipecomponent_set-\d+/, `id_recipecomponent_set-${index}`));
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
    // Only initialize if we're on a page with the cocktail form
    if (document.getElementById('cocktail-form')) {
        new CocktailForm();
    }
});

// Export for testing (Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CocktailForm };
}
