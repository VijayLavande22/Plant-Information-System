/**
 * World Plants - Global Plant Knowledge Hub
 * Main JavaScript file for search functionality and plant display
 */

// Global variables
let allPlants = [];
let filteredPlants = [];

// DOM elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const plantGrid = document.getElementById('plantGrid');
const noResults = document.getElementById('noResults');
const modal = document.getElementById('plantModal');
const modalContent = document.getElementById('modalContent');
const closeBtn = document.querySelector('.close');

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    loadAllPlants();
    setupEventListeners();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search button click
    searchBtn.addEventListener('click', performSearch);
    
    // Enter key in search input
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Live search as user types (with debounce)
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            performSearch();
        }, 300);
    });
    
    // Modal close button
    closeBtn.addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    // Filter items click
    const filterItems = document.querySelectorAll('.filter-item');
    filterItems.forEach(item => {
        item.addEventListener('click', function() {
            // Highlight the clicked filter
            filterItems.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            const filterName = this.querySelector('span').textContent;
            
            // Handle all filter options
            if (filterName === 'Plant Families') {
                loadPlantFamilies();
            } else if (filterName === 'Plant Groups') {
                loadPlantGroups();
            } else if (filterName === 'Plant Categories') {
                loadPlantCategories();
            } else if (filterName === 'Plant Types') {
                loadPlantTypes();
            } else if (filterName === 'Crown Architecture') {
                loadCrownArchitectures();
            } else {
                showNotification(`Filter: ${filterName} - Feature coming soon!`);
            }
        });
    });
}

/**
 * Load all plants from the API
 */
async function loadAllPlants() {
    try {
        showLoading();
        
        const response = await fetch('/api/all-plants');
        if (!response.ok) {
            throw new Error('Failed to load plants');
        }
        
        allPlants = await response.json();
        filteredPlants = [...allPlants];
        
        displayPlants(filteredPlants);
        
    } catch (error) {
        console.error('Error loading plants:', error);
        showError('Failed to load plants. Please refresh the page.');
    }
}

/**
 * Perform search across all data types
 */
async function performSearch() {
    const query = searchInput.value.trim();
    
    try {
        showLoading();
        
        let url = '/api/search';
        if (query) {
            url += `?q=${encodeURIComponent(query)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const results = await response.json();
        displaySearchResults(results);
        
    } catch (error) {
        console.error('Error searching:', error);
        showError('Search failed. Please try again.');
    }
}

/**
 * Display search results from all data types
 */
function displaySearchResults(results) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    const { plants, families, groups, categories, types, architectures } = results;
    
    // Check if any results exist
    const hasResults = plants.length > 0 || families.length > 0 || groups.length > 0 || 
                       categories.length > 0 || types.length > 0 || architectures.length > 0;
    
    if (!hasResults) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Add section headers and cards for each data type
    if (plants.length > 0) {
        addSectionHeader('Plants');
        plants.forEach(plant => {
            plantGrid.appendChild(createPlantCard(plant));
        });
    }
    
    if (families.length > 0) {
        addSectionHeader('Plant Families');
        families.forEach(family => {
            plantGrid.appendChild(createFamilyCard(family));
        });
    }
    
    if (groups.length > 0) {
        addSectionHeader('Plant Groups');
        groups.forEach(group => {
            plantGrid.appendChild(createGroupCard(group));
        });
    }
    
    if (categories.length > 0) {
        addSectionHeader('Plant Categories');
        categories.forEach(category => {
            plantGrid.appendChild(createCategoryCard(category));
        });
    }
    
    if (types.length > 0) {
        addSectionHeader('Plant Types');
        types.forEach(type => {
            plantGrid.appendChild(createTypeCard(type));
        });
    }
    
    if (architectures.length > 0) {
        addSectionHeader('Crown Architecture');
        architectures.forEach(arch => {
            plantGrid.appendChild(createArchitectureCard(arch));
        });
    }
}

/**
 * Add a section header to the grid
 */
function addSectionHeader(title) {
    const header = document.createElement('div');
    header.className = 'search-section-header';
    header.style.cssText = 'grid-column: 1 / -1; font-size: 18px; font-weight: bold; color: #00c853; margin: 20px 0 10px 0; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 5px;';
    header.textContent = title;
    plantGrid.appendChild(header);
}

/**
 * Display plants in the grid
 */
function displayPlants(plants) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (plants.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create plant cards
    plants.forEach(plant => {
        const card = createPlantCard(plant);
        plantGrid.appendChild(card);
    });
}

/**
 * Create a plant card element
 */
function createPlantCard(plant) {
    const card = document.createElement('div');
    card.className = 'plant-card';
    card.setAttribute('data-plant-id', plant.id);
    
    // Get a placeholder image if the URL is invalid
    const imageUrl = plant.image_url || `https://via.placeholder.com/150x150/00c853/ffffff?text=${encodeURIComponent(plant.common_name)}`;
    
    card.innerHTML = `
        <img src="${imageUrl}" 
             alt="${plant.common_name}" 
             onerror="this.src='https://via.placeholder.com/150x150/00c853/ffffff?text=${encodeURIComponent(plant.common_name)}'">
        <h3>${escapeHtml(plant.common_name)}</h3>
        <p>${escapeHtml(plant.scientific_name)}</p>
    `;
    
    // Add click event to open modal
    card.addEventListener('click', () => openPlantModal(plant));
    
    return card;
}

/**
 * Open plant detail modal
 */
function openPlantModal(plant) {
    const imageUrl = plant.image_url || `https://via.placeholder.com/700x300/00c853/ffffff?text=${encodeURIComponent(plant.common_name)}`;
    
    modalContent.innerHTML = `
        <img src="${imageUrl}" 
             alt="${plant.common_name}" 
             class="modal-plant-image"
             onerror="this.src='https://via.placeholder.com/700x300/00c853/ffffff?text=${encodeURIComponent(plant.common_name)}'">
        <h2 class="modal-plant-name">${escapeHtml(plant.common_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(plant.scientific_name)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Family</label>
                <span>${escapeHtml(plant.family || 'N/A')}</span>
            </div>
            <div class="info-item">
                <label>Plant Group</label>
                <span>${escapeHtml(plant.plant_group || 'N/A')}</span>
            </div>
            <div class="info-item">
                <label>Plant Type</label>
                <span>${escapeHtml(plant.plant_type || 'N/A')}</span>
            </div>
            <div class="info-item">
                <label>Distribution</label>
                <span>${escapeHtml(plant.distribution || 'N/A')}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Description</h4>
            <p>${escapeHtml(plant.description || 'No description available.')}</p>
        </div>
    `;
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

/**
 * Load and display Crown Architecture data
 */
async function loadCrownArchitectures() {
    try {
        showLoading();
        
        const response = await fetch('/api/crown-architecture');
        if (!response.ok) {
            throw new Error('Failed to load crown architectures');
        }
        
        const architectures = await response.json();
        displayCrownArchitectures(architectures);
        
    } catch (error) {
        console.error('Error loading crown architectures:', error);
        showError('Failed to load crown architectures. Please try again.');
    }
}

/**
 * Display crown architectures in the grid
 */
function displayCrownArchitectures(architectures) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (architectures.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create architecture cards
    architectures.forEach(arch => {
        const card = createArchitectureCard(arch);
        plantGrid.appendChild(card);
    });
}

/**
 * Create an architecture card element
 */
function createArchitectureCard(arch) {
    const card = document.createElement('div');
    card.className = 'plant-card architecture-card';
    card.innerHTML = `
        <div class="family-icon">
            <i class="fas fa-crown"></i>
        </div>
        <h3>${escapeHtml(arch.architecture_name)}</h3>
        <p>${escapeHtml(arch.description?.substring(0, 60) || '')}...</p>
    `;
    
    // Click to show architecture details
    card.addEventListener('click', function() {
        openArchitectureModal(arch);
    });
    
    return card;
}

/**
 * Open modal with architecture details
 */
function openArchitectureModal(arch) {
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h2 class="modal-plant-name">${escapeHtml(arch.architecture_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(arch.description)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Characteristics</label>
                <span>${escapeHtml(arch.characteristics)}</span>
            </div>
            <div class="info-item">
                <label>Growth Pattern</label>
                <span>${escapeHtml(arch.growth_pattern)}</span>
            </div>
            <div class="info-item">
                <label>Ecological Significance</label>
                <span>${escapeHtml(arch.ecological_significance)}</span>
            </div>
            <div class="info-item">
                <label>Management Considerations</label>
                <span>${escapeHtml(arch.management_considerations)}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Common Species</h4>
            <p>${escapeHtml(arch.common_species)}</p>
        </div>
    `;
    
    // Re-attach close button event
    modalContent.querySelector('.close').addEventListener('click', closeModal);
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}/**
 * Load and display Plant Types data
 */
async function loadPlantTypes() {
    try {
        showLoading();
        
        const response = await fetch('/api/types');
        if (!response.ok) {
            throw new Error('Failed to load plant types');
        }
        
        const types = await response.json();
        displayPlantTypes(types);
        
    } catch (error) {
        console.error('Error loading plant types:', error);
        showError('Failed to load plant types. Please try again.');
    }
}

/**
 * Display plant types in the grid
 */
function displayPlantTypes(types) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (types.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create type cards
    types.forEach(type => {
        const card = createTypeCard(type);
        plantGrid.appendChild(card);
    });
}

/**
 * Create a type card element
 */
function createTypeCard(type) {
    const card = document.createElement('div');
    card.className = 'plant-card type-card';
    card.innerHTML = `
        <div class="family-icon">
            <i class="fas fa-spa"></i>
        </div>
        <h3>${escapeHtml(type.type_name)}</h3>
        <p>${escapeHtml(type.description?.substring(0, 60) || '')}...</p>
    `;
    
    // Click to show type details
    card.addEventListener('click', function() {
        openTypeModal(type);
    });
    
    return card;
}

/**
 * Open modal with type details
 */
function openTypeModal(type) {
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h2 class="modal-plant-name">${escapeHtml(type.type_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(type.description)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Characteristics</label>
                <span>${escapeHtml(type.characteristics)}</span>
            </div>
            <div class="info-item">
                <label>Growth Habits</label>
                <span>${escapeHtml(type.growth_habits)}</span>
            </div>
            <div class="info-item">
                <label>Care Requirements</label>
                <span>${escapeHtml(type.care_requirements)}</span>
            </div>
            <div class="info-item">
                <label>Common Uses</label>
                <span>${escapeHtml(type.common_uses)}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Medicinal Uses</h4>
            <p>${escapeHtml(type.medicinal_uses)}</p>
        </div>
        
        <div class="modal-description">
            <h4>Example Plants</h4>
            <p>${escapeHtml(type.example_plants)}</p>
        </div>
    `;
    
    // Re-attach close button event
    modalContent.querySelector('.close').addEventListener('click', closeModal);
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}/**
 * Load and display Plant Categories data
 */
async function loadPlantCategories() {
    try {
        showLoading();
        
        const response = await fetch('/api/categories');
        if (!response.ok) {
            throw new Error('Failed to load plant categories');
        }
        
        const categories = await response.json();
        displayPlantCategories(categories);
        
    } catch (error) {
        console.error('Error loading plant categories:', error);
        showError('Failed to load plant categories. Please try again.');
    }
}

/**
 * Display plant categories in the grid
 */
function displayPlantCategories(categories) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (categories.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create category cards
    categories.forEach(category => {
        const card = createCategoryCard(category);
        plantGrid.appendChild(card);
    });
}

/**
 * Create a category card element
 */
function createCategoryCard(category) {
    const card = document.createElement('div');
    card.className = 'plant-card category-card';
    card.innerHTML = `
        <div class="family-icon">
            <i class="fas fa-layer-group"></i>
        </div>
        <h3>${escapeHtml(category.category_name)}</h3>
        <p>${escapeHtml(category.description?.substring(0, 60) || '')}...</p>
    `;
    
    // Click to show category details
    card.addEventListener('click', function() {
        openCategoryModal(category);
    });
    
    return card;
}

/**
 * Open modal with category details
 */
function openCategoryModal(category) {
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h2 class="modal-plant-name">${escapeHtml(category.category_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(category.description)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Characteristics</label>
                <span>${escapeHtml(category.characteristics)}</span>
            </div>
            <div class="info-item">
                <label>Distribution</label>
                <span>${escapeHtml(category.distribution)}</span>
            </div>
            <div class="info-item">
                <label>Economic Importance</label>
                <span>${escapeHtml(category.economic_importance)}</span>
            </div>
            <div class="info-item">
                <label>Medicinal Uses</label>
                <span>${escapeHtml(category.medicinal_uses)}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Example Plants</h4>
            <p>${escapeHtml(category.example_plants)}</p>
        </div>
    `;
    
    // Re-attach close button event
    modalContent.querySelector('.close').addEventListener('click', closeModal);
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}/**
 * Load and display Plant Groups data
 */
async function loadPlantGroups() {
    try {
        showLoading();
        
        const response = await fetch('/api/groups');
        if (!response.ok) {
            throw new Error('Failed to load plant groups');
        }
        
        const groups = await response.json();
        displayPlantGroups(groups);
        
    } catch (error) {
        console.error('Error loading plant groups:', error);
        showError('Failed to load plant groups. Please try again.');
    }
}

/**
 * Display plant groups in the grid
 */
function displayPlantGroups(groups) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (groups.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create group cards
    groups.forEach(group => {
        const card = createGroupCard(group);
        plantGrid.appendChild(card);
    });
}

/**
 * Create a group card element
 */
function createGroupCard(group) {
    const card = document.createElement('div');
    card.className = 'plant-card group-card';
    card.innerHTML = `
        <div class="family-icon">
            <i class="fas fa-leaf"></i>
        </div>
        <h3>${escapeHtml(group.group_name)}</h3>
        <p>${escapeHtml(group.description?.substring(0, 60) || '')}...</p>
    `;
    
    // Click to show group details
    card.addEventListener('click', function() {
        openGroupModal(group);
    });
    
    return card;
}

/**
 * Open modal with group details
 */
function openGroupModal(group) {
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h2 class="modal-plant-name">${escapeHtml(group.group_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(group.description)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Characteristics</label>
                <span>${escapeHtml(group.characteristics)}</span>
            </div>
            <div class="info-item">
                <label>Distribution</label>
                <span>${escapeHtml(group.distribution)}</span>
            </div>
            <div class="info-item">
                <label>Economic Importance</label>
                <span>${escapeHtml(group.economic_importance)}</span>
            </div>
            <div class="info-item">
                <label>Medicinal Uses</label>
                <span>${escapeHtml(group.medicinal_uses)}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Example Plants</h4>
            <p>${escapeHtml(group.example_plants)}</p>
        </div>
    `;
    
    // Re-attach close button event
    modalContent.querySelector('.close').addEventListener('click', closeModal);
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}/**
 * Close the modal
 */
function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Show loading state
 */
function showLoading() {
    plantGrid.innerHTML = `
        <div class="loading-container" style="grid-column: 1/-1; text-align: center; padding: 60px;">
            <i class="fas fa-spinner fa-spin" style="font-size: 48px; color: #00c853;"></i>
            <p style="margin-top: 20px; color: #666;">Loading plants...</p>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(message) {
    plantGrid.innerHTML = `
        <div class="error-container" style="grid-column: 1/-1; text-align: center; padding: 60px;">
            <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #ff5722;"></i>
            <p style="margin-top: 20px; color: #666;">${escapeHtml(message)}</p>
        </div>
    `;
}

/**
 * Show notification toast
 */
function showNotification(message) {
    // Remove existing notification
    const existing = document.querySelector('.notification-toast');
    if (existing) {
        existing.remove();
    }
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = 'notification-toast';
    notification.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #00c853;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

/**
 * Load and display Plant Families data
 */
async function loadPlantFamilies() {
    try {
        showLoading();
        
        const response = await fetch('/api/families');
        if (!response.ok) {
            throw new Error('Failed to load plant families');
        }
        
        const families = await response.json();
        displayPlantFamilies(families);
        
    } catch (error) {
        console.error('Error loading plant families:', error);
        showError('Failed to load plant families. Please try again.');
    }
}

/**
 * Display plant families in the grid
 */
function displayPlantFamilies(families) {
    // Clear the grid
    plantGrid.innerHTML = '';
    
    // Show/hide no results message
    if (families.length === 0) {
        plantGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    plantGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Create family cards
    families.forEach(family => {
        const card = createFamilyCard(family);
        plantGrid.appendChild(card);
    });
}

/**
 * Create a family card element
 */
function createFamilyCard(family) {
    const card = document.createElement('div');
    card.className = 'plant-card family-card';
    card.innerHTML = `
        <div class="family-icon">
            <i class="fas fa-seedling"></i>
        </div>
        <h3>${escapeHtml(family.family_name)}</h3>
        <p>${escapeHtml(family.common_name)}</p>
        <div class="family-details" style="display: none; margin-top: 10px; font-size: 12px; color: #666; text-align: left;">
            <p><strong>Characteristics:</strong> ${escapeHtml(family.characteristics?.substring(0, 80) || 'N/A')}...</p>
            <p><strong>Examples:</strong> ${escapeHtml(family.example_plants || 'N/A')}</p>
        </div>
    `;
    
    // Click to show family details
    card.addEventListener('click', function() {
        openFamilyModal(family);
    });
    
    return card;
}

/**
 * Open modal with family details
 */
function openFamilyModal(family) {
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h2 class="modal-plant-name">${escapeHtml(family.family_name)}</h2>
        <p class="modal-plant-scientific">${escapeHtml(family.common_name)}</p>
        
        <div class="modal-plant-info">
            <div class="info-item">
                <label>Description</label>
                <span>${escapeHtml(family.description)}</span>
            </div>
            <div class="info-item">
                <label>Characteristics</label>
                <span>${escapeHtml(family.characteristics)}</span>
            </div>
            <div class="info-item">
                <label>Distribution</label>
                <span>${escapeHtml(family.distribution)}</span>
            </div>
            <div class="info-item">
                <label>Economic Importance</label>
                <span>${escapeHtml(family.economic_importance)}</span>
            </div>
        </div>
        
        <div class="modal-description">
            <h4>Medicinal Uses</h4>
            <p>${escapeHtml(family.medicinal_uses)}</p>
        </div>
        
        <div class="modal-description">
            <h4>Example Plants</h4>
            <p>${escapeHtml(family.example_plants)}</p>
        </div>
    `;
    
    // Re-attach close button event
    modalContent.querySelector('.close').addEventListener('click', closeModal);
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}
