document.addEventListener('DOMContentLoaded', function() {
    function updateSelectStyles() {
        const selects = document.querySelectorAll('select.form-select');
        selects.forEach(select => {
            if (select.value !== '0') {
                select.classList.add('form-select-changed');
            } else {
                select.classList.remove('form-select-changed');
            }
        });
    }

    updateAllSliderBackgrounds();
    updateSelectStyles();
    
    function updateSliderBackground(slider) {
        if (!slider) return;
        const min = parseFloat(slider.min) || 0;
        const max = parseFloat(slider.max) || 100;
        const value = parseFloat(slider.value) || 0;
        const percentage = ((value - min) / (max - min)) * 100;
        slider.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percentage}%, #e2e8f0 ${percentage}%, #e2e8f0 100%)`;
    }
    
    function updateAllSliderBackgrounds() {
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(updateSliderBackground);
    }
    
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            updateSliderBackground(this);
            const valueId = this.id.replace('adjust', '') + 'Value';
            const valueDisplay = document.getElementById(valueId);
            if (valueDisplay) {
                valueDisplay.textContent = this.value;
            }
        });
    });

    const selects = document.querySelectorAll('select.form-select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            // Update the text value display
            const valueId = this.id.replace('adjust', '') + 'Value';
            const valueDisplay = document.getElementById(valueId);
            if (valueDisplay) {
                valueDisplay.textContent = this.value;
            }
            updateSelectStyles();
        });
    });
    
    // Download button functionality
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const syntheticImg = document.getElementById('syntheticImg');
            if (!syntheticImg || !syntheticImg.src) {
                alert('No customized image available to download.');
                return;
            }

            const downloadLink = document.createElement('a');
            downloadLink.href = syntheticImg.src;

            downloadLink.download = 'customized_face.png';

            // Append to body, click, and then remove
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    }
    
    // Reset button functionality
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // ... (code to set all control values to default remains the same) ...
            document.getElementById('adjustTruncation').value = '0.5';
            document.getElementById('adjustNoiseStrength').value = '1.0';
            document.getElementById('adjustAge').value = '0';
            document.getElementById('adjustGender').value = '0';
            document.getElementById('adjustSmile').value = '0';
            document.getElementById('adjustLighting').value = '0';
            document.getElementById('adjustHairColor').value = '0';
            document.getElementById('adjustHairLength').value = '0';
            document.getElementById('adjustExpression').value = '0';
            document.getElementById('adjustEyeColor').value = '0';
            document.getElementById('adjustEyeState').value = '0';
            document.getElementById('adjustSeriousMood').value = '0';
            document.getElementById('adjustMaturity').value = '0';
            document.getElementById('truncationValue').textContent = '0.5';
            document.getElementById('noiseValue').textContent = '1.0';
            document.getElementById('ageValue').textContent = '0';
            document.getElementById('genderValue').textContent = '0';
            document.getElementById('smileValue').textContent = '0';
            document.getElementById('lightingValue').textContent = '0';
            document.getElementById('hairColorValue').textContent = '0';
            document.getElementById('hairLengthValue').textContent = '0';
            document.getElementById('expressionValue').textContent = '0';
            document.getElementById('eyeColorValue').textContent = '0';
            document.getElementById('eyeStateValue').textContent = '0';
            document.getElementById('seriousMoodValue').textContent = '0';
            document.getElementById('maturityValue').textContent = '0';

            updateAllSliderBackgrounds();
            updateSelectStyles();
        });
    }
    
    // Apply Changes button functionality
    const applyChangesBtn = document.getElementById('applyChangesBtn');
    if (applyChangesBtn) {
        applyChangesBtn.addEventListener('click', function() {
            if (!document.getElementById('syntheticImg') || !document.getElementById('syntheticImg').src) {
                alert('No synthetic image found. Please generate a face first.');
                return;
            }

            document.getElementById('syntheticImg').scrollIntoView({ behavior: 'smooth', block: 'center' });

            // ... (rest of the logic for collecting data and fetch remains the same) ...
            const combinedSliderValue = parseFloat(document.getElementById('adjustAge').value);
            let pose_attribute_value = 0.0;
            let age_attribute_value = 0.0;
            if (combinedSliderValue <= 0) {
                pose_attribute_value = 0.0; 
                age_attribute_value = combinedSliderValue;
            } else {
                pose_attribute_value = -combinedSliderValue;
                age_attribute_value = 0.0; 
            }
            const customizationData = {
                truncation: parseFloat(document.getElementById('adjustTruncation').value),
                noise_strength: parseFloat(document.getElementById('adjustNoiseStrength').value),
                age: age_attribute_value,
                pose: pose_attribute_value,
                gender: parseFloat(document.getElementById('adjustGender').value),
                smile: parseFloat(document.getElementById('adjustSmile').value),
                lighting: parseFloat(document.getElementById('adjustLighting').value),
                hair_color: parseFloat(document.getElementById('adjustHairColor').value),
                hair_length: parseFloat(document.getElementById('adjustHairLength').value),
                expression: parseFloat(document.getElementById('adjustExpression').value),
                eye_color: parseFloat(document.getElementById('adjustEyeColor').value),
                eye_state: parseFloat(document.getElementById('adjustEyeState').value),
                serious_mood: parseFloat(document.getElementById('adjustSeriousMood').value),
                maturity: parseFloat(document.getElementById('adjustMaturity').value)
            };
            document.getElementById('customizationLoadingIndicator').style.display = 'block';
            fetch('/customize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(customizationData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.synthetic_image) {
                    document.getElementById('syntheticImg').src = data.synthetic_image;
                }
                document.getElementById('truncationValue').textContent = customizationData.truncation;
                document.getElementById('noiseValue').textContent = customizationData.noise_strength;
                document.getElementById('genderValue').textContent = customizationData.gender;
                document.getElementById('smileValue').textContent = customizationData.smile;
                document.getElementById('lightingValue').textContent = customizationData.lighting;
                document.getElementById('hairColorValue').textContent = customizationData.hair_color;
                document.getElementById('hairLengthValue').textContent = customizationData.hair_length;
                document.getElementById('expressionValue').textContent = customizationData.expression;
                document.getElementById('eyeColorValue').textContent = customizationData.eye_color;
                document.getElementById('eyeStateValue').textContent = customizationData.eye_state;
                document.getElementById('seriousMoodValue').textContent = customizationData.serious_mood;
                document.getElementById('maturityValue').textContent = customizationData.maturity;
                document.getElementById('customizationLoadingIndicator').style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while processing your request. Please try again.');
                document.getElementById('customizationLoadingIndicator').style.display = 'none';
            });
        });
    }
});