/**
 * Tests for CocktailForm class
 * Tests dynamic ingredient form management and expansion functionality
 */

// Import the class (we'll need to modify our JS files to support this)
// For now, we'll load the file and test the global functions

describe('CocktailForm', () => {
    let cocktailFormHTML;
    
    beforeEach(() => {
        // Create a mock cocktail form DOM structure
        cocktailFormHTML = `
            <form id="cocktail-form">
                <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
                
                <!-- Management form fields -->
                <input type="hidden" id="id_recipecomponent_set-TOTAL_FORMS" value="3">
                <input type="hidden" id="id_recipecomponent_set-MAX_NUM_FORMS" value="15">
                
                <!-- Ingredient forms container -->
                <div id="ingredient-forms">
                    <div class="ingredient-row" id="ingredient-0">
                        <select name="recipecomponent_set-0-ingredient" id="id_recipecomponent_set-0-ingredient">
                            <option value="">Select ingredient...</option>
                            <option value="1">Gin</option>
                            <option value="new_ingredient">+ Create New Ingredient</option>
                        </select>
                        <input type="number" name="recipecomponent_set-0-amount" id="id_recipecomponent_set-0-amount">
                        <select name="recipecomponent_set-0-unit" id="id_recipecomponent_set-0-unit">
                            <option value="oz">oz</option>
                        </select>
                        <input type="text" name="recipecomponent_set-0-preparation_note" id="id_recipecomponent_set-0-preparation_note">
                        <input type="number" name="recipecomponent_set-0-order" id="id_recipecomponent_set-0-order" value="0">
                        <input type="checkbox" name="recipecomponent_set-0-DELETE" id="id_recipecomponent_set-0-DELETE">
                    </div>
                    
                    <div class="ingredient-row" id="ingredient-1">
                        <select name="recipecomponent_set-1-ingredient" id="id_recipecomponent_set-1-ingredient">
                            <option value="">Select ingredient...</option>
                            <option value="2">Tonic Water</option>
                            <option value="new_ingredient">+ Create New Ingredient</option>
                        </select>
                        <input type="number" name="recipecomponent_set-1-amount" id="id_recipecomponent_set-1-amount">
                        <select name="recipecomponent_set-1-unit" id="id_recipecomponent_set-1-unit">
                            <option value="oz">oz</option>
                        </select>
                        <input type="text" name="recipecomponent_set-1-preparation_note" id="id_recipecomponent_set-1-preparation_note">
                        <input type="number" name="recipecomponent_set-1-order" id="id_recipecomponent_set-1-order" value="1">
                        <input type="checkbox" name="recipecomponent_set-1-DELETE" id="id_recipecomponent_set-1-DELETE">
                    </div>
                </div>
                
                <!-- Add ingredient button -->
                <button type="button" id="add-ingredient-btn">Add More Ingredients</button>
                
                <!-- New ingredient modal -->
                <div id="newIngredientModal" class="modal">
                    <form id="quick-ingredient-form">
                        <input type="text" id="new-ingredient-name" name="name">
                        <select id="new-ingredient-type" name="ingredient_type">
                            <option value="spirit">Spirit</option>
                        </select>
                        <input type="number" id="new-ingredient-alcohol" name="alcohol_content" value="0">
                        <textarea id="new-ingredient-description" name="description"></textarea>
                    </form>
                    <button type="button" id="save-new-ingredient">Save</button>
                </div>
            </form>
        `;
        
        createTestDOM(cocktailFormHTML);
        
        // Load the cocktail form script
        require('../cocktail-form.js');
    });
    
    describe('Initialization', () => {
        test('should initialize CocktailForm when form exists', () => {
            expect(document.getElementById('cocktail-form')).toBeTruthy();
            expect(document.getElementById('add-ingredient-btn')).toBeTruthy();
        });
        
        test('should read initial form count correctly', () => {
            const totalFormsInput = document.getElementById('id_recipecomponent_set-TOTAL_FORMS');
            expect(totalFormsInput.value).toBe('3');
        });
        
        test('should read max forms limit correctly', () => {
            const maxFormsInput = document.getElementById('id_recipecomponent_set-MAX_NUM_FORMS');
            expect(maxFormsInput.value).toBe('15');
        });
    });
    
    describe('Add Ingredient Functionality', () => {
        test('should add new ingredient form when button clicked', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            const initialRows = document.querySelectorAll('.ingredient-row').length;
            
            simulateEvent(addButton, 'click');
            
            const newRows = document.querySelectorAll('.ingredient-row').length;
            expect(newRows).toBe(initialRows + 1);
        });
        
        test('should update total forms count when adding ingredient', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            const totalFormsInput = document.getElementById('id_recipecomponent_set-TOTAL_FORMS');
            
            simulateEvent(addButton, 'click');
            
            expect(totalFormsInput.value).toBe('4');
        });
        
        test('should update form indices correctly', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            
            simulateEvent(addButton, 'click');
            
            const newRow = document.querySelector('#ingredient-3');
            expect(newRow).toBeTruthy();
            
            const newSelect = newRow.querySelector('select[name="recipecomponent_set-3-ingredient"]');
            expect(newSelect).toBeTruthy();
        });
        
        test('should disable button when max forms reached', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            const maxFormsInput = document.getElementById('id_recipecomponent_set-MAX_NUM_FORMS');
            maxFormsInput.value = '3'; // Set low limit for testing
            
            // Should still be enabled at start
            expect(addButton.disabled).toBe(false);
            
            // Add one more to reach limit
            simulateEvent(addButton, 'click');
            
            // Should now be disabled
            expect(addButton.disabled).toBe(true);
            expect(addButton.textContent).toContain('Maximum ingredients reached');
        });
        
        test('should clear form values in new ingredient row', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            
            // Set a value in the template row
            const firstRow = document.querySelector('.ingredient-row');
            const firstSelect = firstRow.querySelector('select');
            firstSelect.value = '1';
            
            simulateEvent(addButton, 'click');
            
            // New row should have empty values
            const newRow = document.querySelector('#ingredient-3');
            const newSelect = newRow.querySelector('select');
            expect(newSelect.value).toBe('');
        });
    });
    
    describe('New Ingredient Creation', () => {
        test('should show modal when "Create New Ingredient" selected', () => {
            const ingredientSelect = document.getElementById('id_recipecomponent_set-0-ingredient');
            const modal = document.getElementById('newIngredientModal');
            
            ingredientSelect.value = 'new_ingredient';
            simulateEvent(ingredientSelect, 'change');
            
            // Check if Bootstrap modal show was called
            expect(bootstrap.Modal).toHaveBeenCalledWith(modal);
        });
        
        test('should reset select value when showing modal', () => {
            const ingredientSelect = document.getElementById('id_recipecomponent_set-0-ingredient');
            
            ingredientSelect.value = 'new_ingredient';
            simulateEvent(ingredientSelect, 'change');
            
            expect(ingredientSelect.value).toBe('');
        });
        
        test('should handle successful ingredient creation', async () => {
            const saveButton = document.getElementById('save-new-ingredient');
            const nameInput = document.getElementById('new-ingredient-name');
            const typeSelect = document.getElementById('new-ingredient-type');
            
            // Set up form data
            nameInput.value = 'Test Gin';
            typeSelect.value = 'spirit';
            
            // Mock successful API response
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    ingredient: {
                        id: 99,
                        name: 'Test Gin',
                        type_display: 'Spirit'
                    }
                })
            });
            
            simulateEvent(saveButton, 'click');
            
            // Wait for async operations
            await waitFor(() => fetch.mock.calls.length > 0);
            
            expect(fetch).toHaveBeenCalledWith(
                '/test/ingredients/add/',
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-csrf-token'
                    })
                })
            );
        });
        
        test('should handle ingredient creation errors', async () => {
            const saveButton = document.getElementById('save-new-ingredient');
            
            // Mock error response
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: false,
                    error: 'Ingredient already exists'
                })
            });
            
            // Mock alert
            global.alert = jest.fn();
            
            simulateEvent(saveButton, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            expect(global.alert).toHaveBeenCalledWith(
                'Error creating ingredient: Ingredient already exists'
            );
        });
    });
    
    describe('Form Validation', () => {
        test('should handle DELETE checkbox changes', () => {
            const deleteCheckbox = document.getElementById('id_recipecomponent_set-0-DELETE');
            const addButton = document.getElementById('add-ingredient-btn');
            
            // Check delete checkbox
            deleteCheckbox.checked = true;
            simulateEvent(deleteCheckbox, 'change');
            
            // Button should reflect the change
            expect(addButton.disabled).toBe(false);
        });
        
        test('should update button text based on remaining slots', () => {
            const addButton = document.getElementById('add-ingredient-btn');
            const maxFormsInput = document.getElementById('id_recipecomponent_set-MAX_NUM_FORMS');
            maxFormsInput.value = '4'; // Set to 4 for testing
            
            simulateEvent(addButton, 'click');
            
            expect(addButton.textContent).toContain('1 remaining');
        });
    });
});
