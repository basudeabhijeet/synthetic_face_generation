document.addEventListener('DOMContentLoaded', function() {
    sessionStorage.setItem('lastProductDetailPage', window.location.href);
    const showcase = document.getElementById('imageShowcase');
    if (!showcase) return;

    const images = JSON.parse(showcase.dataset.images);
    const labels = JSON.parse(showcase.dataset.labels);
    
    let currentIndex = 0;

    const carouselImage = document.getElementById('carouselImage');
    const imageLabel = document.getElementById('imageLabel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    function updateCarousel() {
        const currentImageUrl = images[currentIndex];
        carouselImage.src = currentImageUrl + '?t=' + new Date().getTime();
        imageLabel.textContent = labels[currentIndex];
        
        prevBtn.style.display = currentIndex === 0 ? 'none' : 'flex';
        nextBtn.style.display = currentIndex === images.length - 1 ? 'none' : 'flex';
    }

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            updateCarousel();
        }
    });

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const imageUrlToDownload = images[currentIndex];
            
            // Create a temporary link element to trigger the download
            const link = document.createElement('a');
            link.href = imageUrlToDownload;
            
            // Suggest a filename for the download
            link.download = `generated_image_${currentIndex}.png`;
            
            // Append to body, click, and then remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    // Initial setup when the page loads
    updateCarousel();
});