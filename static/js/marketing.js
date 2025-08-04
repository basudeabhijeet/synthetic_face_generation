document.addEventListener('DOMContentLoaded', function() {
    sessionStorage.removeItem('lastProductDetailPage');
    const showBtn = document.getElementById('showProductsBtn');
    const otherProductsPanel = document.getElementById('otherProductsPanel');

    // On page load, check and apply the saved state from the browser session
    const savedState = sessionStorage.getItem('productsPanelState');
    if (savedState === 'block') { 
        otherProductsPanel.style.display = 'block';
        if(showBtn) showBtn.textContent = 'Hide Available Products';
    }

    if (showBtn) {
        showBtn.addEventListener('click', function() {
            const isHidden = otherProductsPanel.style.display === 'none';
            const newState = isHidden ? 'block' : 'none';

            // Apply the new state to the page
            otherProductsPanel.style.display = newState;
            this.textContent = isHidden ? 'Hide Available Products' : 'Show Available Products';
            
            // Save the new state in the browser session
            sessionStorage.setItem('productsPanelState', newState);
        });
    }

    
    // Find all links wrapping the product cards
    const productLinks = document.querySelectorAll('.controls-grid a');

    productLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const card = this.querySelector('.card');
            if (card) {
                // Add a specific class to the card for styling
                card.classList.add('active'); 
            }
        });
    });
});