function filterByName() {
    const searchQuery = document.getElementById('search-by-name').value.toLowerCase();
    const recipeCards = document.querySelectorAll('.recipe-card');

    recipeCards.forEach(card => {
        const name = card.getAttribute('recipe-name');
        if (name.includes(searchQuery)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
};

function filterByCuisine() {
    const filterValue = document.getElementById('cuisine-filter').value.toLowerCase();
    const recipeCards = document.querySelectorAll('.recipe-card');

    recipeCards.forEach(card => {
        const category = card.getAttribute('recipe-cuisine');
        if (filterValue === 'all' || category === filterValue) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function filterByCategory() {
    const filterValue = document.getElementById('category-filter').value.toLowerCase();
    const recipeCards = document.querySelectorAll('.recipe-card');

    recipeCards.forEach(card => {
        const category = card.getAttribute('recipe-category');
        if (filterValue === 'all' || category === filterValue) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}