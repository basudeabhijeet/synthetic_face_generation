document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const preview = document.getElementById('preview');
            preview.innerHTML = '';
            if (this.files && this.files[0]) {
                document.getElementById('generateBtnContainer').style.display = 'flex';
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    preview.appendChild(img);
                    document.getElementById('resultsCard').style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('errorMessage').style.display = 'none';
        });
    }
    
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const syntheticImg = document.getElementById('syntheticImg');
            if (!syntheticImg || !syntheticImg.src) {
                alert('No synthetic image available to download.');
                return;
            }
            const downloadLink = document.createElement('a');
            downloadLink.href = syntheticImg.src;
            downloadLink.download = 'synthetic_face.png';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    }
    
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        dropZone.addEventListener('drop', handleDrop, false);
    }
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropZone.classList.add('highlight');
        dropZone.style.borderColor = 'var(--primary-color)';
        dropZone.style.backgroundColor = 'rgba(74, 111, 216, 0.08)';
    }
    
    function unhighlight() {
        dropZone.classList.remove('highlight');
        dropZone.style.borderColor = 'var(--border-color)';
        dropZone.style.backgroundColor = '';
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length) {
            const fileInput = document.getElementById('fileInput');
            fileInput.files = files;
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
    
    const fileButton = document.querySelector('.btn-outline');
    if (fileButton) {
        fileButton.addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
    }

    const resultsCard = document.getElementById('resultsCard');
    if (resultsCard && resultsCard.style.display === 'block') {
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});