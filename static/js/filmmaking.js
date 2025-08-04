document.addEventListener('DOMContentLoaded', function() {
    const applyButtons = document.querySelectorAll('.apply-scene-btn');
    const sceneImage = document.getElementById('sceneImg');
    const loadingIndicator = document.getElementById('sceneLoadingIndicator');
    const resetBtn = document.getElementById('resetSceneBtn');
    
    const presetCards = document.querySelectorAll('.preset-card');
    
    // Store the original image source when the page loads
    const originalImageSrc = sceneImage.src;

    applyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const edits = JSON.parse(this.dataset.edits);

            // Automatically scroll up to the image container
            sceneImage.scrollIntoView({ behavior: 'smooth', block: 'center' });

            
            presetCards.forEach(card => card.classList.remove('active'));
            this.closest('.preset-card').classList.add('active');

            // Show loading indicator
            loadingIndicator.style.display = 'block';
            sceneImage.style.filter = 'blur(5px)';

            fetch('/apply_scene', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ edits: edits }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.new_image_url) {
                    sceneImage.src = data.new_image_url;
                } else if (data.error) {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while applying the scene.');
                presetCards.forEach(card => card.classList.remove('active'));
            })
            .finally(() => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                sceneImage.style.filter = 'none';
            });
        });
    });

    // Add event listener for the reset button
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Reset the image source
            sceneImage.src = originalImageSrc;
            
            presetCards.forEach(card => card.classList.remove('active'));
        });
    }
});