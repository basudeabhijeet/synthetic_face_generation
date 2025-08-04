document.addEventListener('DOMContentLoaded', function() {
    // Check if a 'lastProductDetailPage' URL is stored in the session
    const lastProductPage = sessionStorage.getItem('lastProductDetailPage');
    
    // Find the 'Marketing' link in the navigation bar
    const marketingLink = document.querySelector('a.nav-link[href="/marketing"]');

    // If a stored URL exists and the link is found, update the link's href
    if (lastProductPage && marketingLink) {
        marketingLink.href = lastProductPage;
    }
});