// Main JavaScript for PixelIQ Result Generator

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // File input preview
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            const fileLabel = document.querySelector('.custom-file-label');
            if (fileLabel && fileName) {
                fileLabel.textContent = fileName;
            }
        });
    }

    // Subject selection enhancement
    const subjectSelect = document.querySelector('select[name="subject_columns"]');
    if (subjectSelect) {
        // Add search functionality
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-2';
        searchInput.placeholder = 'Search subjects...';
        searchInput.style.marginBottom = '10px';
        
        subjectSelect.parentNode.insertBefore(searchInput, subjectSelect);
        
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const options = subjectSelect.options;
            
            for (let i = 0; i < options.length; i++) {
                const optionText = options[i].text.toLowerCase();
                const match = optionText.includes(searchTerm);
                options[i].style.display = match ? '' : 'none';
            }
        });
    }

    // Preview button click handler
    const previewBtn = document.querySelector('.preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Add loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating Preview...';
            this.disabled = true;
            
            // Submit form
            this.closest('form').submit();
        });
    }

    // Generate PDF button
    const generateBtn = document.querySelector('.generate-pdf-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', function(e) {
            const confirmed = confirm('Generate PDF for all students? This may take a moment.');
            if (!confirmed) {
                e.preventDefault();
            } else {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating PDF...';
                this.disabled = true;
            }
        });
    }

    // Copy text to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const text = this.getAttribute('data-text');
            navigator.clipboard.writeText(text).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check text-success"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Smooth scroll to sections
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Track button clicks for analytics
    const trackButtons = document.querySelectorAll('[data-track]');
    trackButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const event = this.getAttribute('data-track');
            console.log('Analytics Event:', event);
            // You can send this to Google Analytics or your analytics service
        });
    });

    // Quick tips tooltip
    const tips = document.querySelectorAll('[data-tip]');
    tips.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tip = this.getAttribute('data-tip');
            const tooltip = document.createElement('div');
            tooltip.className = 'position-absolute bg-dark text-white p-2 rounded shadow';
            tooltip.style.fontSize = '12px';
            tooltip.style.whiteSpace = 'nowrap';
            tooltip.textContent = tip;
            tooltip.style.top = '-30px';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translateX(-50%)';
            
            this.style.position = 'relative';
            this.appendChild(tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.position-absolute');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});

// Utility function for form validation
function validateFileSize(fileInput, maxSizeMB = 10) {
    const file = fileInput.files[0];
    if (!file) return true;
    
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        alert(`File size exceeds ${maxSizeMB}MB limit. Please upload a smaller file.`);
        fileInput.value = '';
        return false;
    }
    return true;
}

// Utility function for PDF download tracking
function trackPDFDownload(studentCount) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'pdf_download', {
            'event_category': 'Generation',
            'event_label': `${studentCount} students`,
            'value': studentCount
        });
    }
}

console.log('PixelIQ Result Generator loaded successfully!');