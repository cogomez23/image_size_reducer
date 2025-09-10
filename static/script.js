// JavaScript for Image Size Reducer Web App

class ImageReducerApp {
    constructor() {
        this.selectedFiles = [];
        this.processedResults = [];
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.maxSizeInput = document.getElementById('maxSize');
        this.processBtn = document.getElementById('processBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsSummary = document.getElementById('resultsSummary');
        this.resultsList = document.getElementById('resultsList');
        this.downloadAllBtn = document.getElementById('downloadAllBtn');
    }

    attachEventListeners() {
        // File input and drop zone
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // Size presets
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePresetClick(e));
        });

        // Max size input
        this.maxSizeInput.addEventListener('input', () => this.updatePresetButtons());

        // Control buttons
        this.processBtn.addEventListener('click', () => this.processImages());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        this.downloadAllBtn.addEventListener('click', () => this.downloadAll());
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.addFiles(files);
    }

    handleDragOver(event) {
        event.preventDefault();
        this.dropZone.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.preventDefault();
        this.dropZone.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        this.dropZone.classList.remove('dragover');
        const files = Array.from(event.dataTransfer.files);
        this.addFiles(files);
    }

    handlePresetClick(event) {
        const size = parseFloat(event.target.dataset.size);
        this.maxSizeInput.value = size;
        this.updatePresetButtons();
    }

    updatePresetButtons() {
        const currentSize = parseFloat(this.maxSizeInput.value);
        document.querySelectorAll('.preset-btn').forEach(btn => {
            const btnSize = parseFloat(btn.dataset.size);
            btn.classList.toggle('active', Math.abs(btnSize - currentSize) < 0.01);
        });
    }

    addFiles(files) {
        const imageFiles = files.filter(file => file.type.startsWith('image/'));

        imageFiles.forEach(file => {
            // Check if file already exists
            const exists = this.selectedFiles.some(f =>
                f.name === file.name && f.size === file.size
            );

            if (!exists) {
                this.selectedFiles.push(file);
            }
        });

        this.updateFileList();
        this.updateProcessButton();
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.updateProcessButton();
    }

    updateFileList() {
        if (this.selectedFiles.length === 0) {
            this.fileList.innerHTML = '';
            return;
        }

        this.fileList.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <i class="fas fa-image"></i>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${this.formatFileSize(file.size)} • ${file.type}</p>
                    </div>
                </div>
                <button class="file-remove" onclick="app.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    updateProcessButton() {
        this.processBtn.disabled = this.selectedFiles.length === 0;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async processImages() {
        if (this.selectedFiles.length === 0) return;

        const maxSize = parseFloat(this.maxSizeInput.value);
        if (isNaN(maxSize) || maxSize <= 0) {
            this.showError('Please enter a valid target size (must be greater than 0)');
            return;
        }

        this.showProgress();
        this.processBtn.disabled = true;

        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        formData.append('max_size', maxSize);

        try {
            this.updateProgress(0, 'Uploading files...');

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.updateProgress(100, 'Processing complete!');
            setTimeout(() => {
                this.hideProgress();
                this.showResults(data.results);
            }, 1000);

        } catch (error) {
            console.error('Error processing images:', error);
            this.hideProgress();
            this.showError(`Error processing images: ${error.message}`);
        } finally {
            this.processBtn.disabled = false;
        }
    }

    showProgress() {
        this.progressSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
    }

    updateProgress(percentage, text) {
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = text;
    }

    showResults(results) {
        this.processedResults = results;

        // Calculate summary statistics
        const successful = results.filter(r => !r.error);
        const failed = results.filter(r => r.error);

        const totalOriginalSize = successful.reduce((sum, r) => sum + r.original_size_mb, 0);
        const totalFinalSize = successful.reduce((sum, r) => sum + r.final_size_mb, 0);
        const totalReduction = totalOriginalSize > 0 ? ((totalOriginalSize - totalFinalSize) / totalOriginalSize) * 100 : 0;

        // Show summary
        this.resultsSummary.innerHTML = `
            <h3>Processing Summary</h3>
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="stat-value">${successful.length}</span>
                    <span class="stat-label">Successfully processed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${failed.length}</span>
                    <span class="stat-label">Failed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${totalOriginalSize.toFixed(2)} MB</span>
                    <span class="stat-label">Original total size</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${totalFinalSize.toFixed(2)} MB</span>
                    <span class="stat-label">Final total size</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${totalReduction.toFixed(1)}%</span>
                    <span class="stat-label">Total reduction</span>
                </div>
            </div>
        `;

        // Show individual results
        this.resultsList.innerHTML = results.map(result => {
            if (result.error) {
                return `
                    <div class="result-item error">
                        <div class="result-info">
                            <h4>${result.original_filename}</h4>
                            <p style="color: #dc3545;"><i class="fas fa-exclamation-triangle"></i> ${result.error}</p>
                        </div>
                    </div>
                `;
            }

            return `
                <div class="result-item">
                    <div class="result-info">
                        <h4>${result.original_filename}</h4>
                        <div class="result-stats">
                            <div class="result-stat">
                                <span class="result-stat-value">${result.original_size_mb.toFixed(2)} MB</span>
                                <span class="result-stat-label">Original</span>
                            </div>
                            <div class="result-stat">
                                <span class="result-stat-value">${result.final_size_mb.toFixed(2)} MB</span>
                                <span class="result-stat-label">Final</span>
                            </div>
                            <div class="result-stat">
                                <span class="result-stat-value">${result.reduction_percentage.toFixed(1)}%</span>
                                <span class="result-stat-label">Reduction</span>
                            </div>
                            <div class="result-stat">
                                <span class="result-stat-value">${result.quality_used}%</span>
                                <span class="result-stat-label">Quality</span>
                            </div>
                            <div class="result-stat">
                                <span class="result-stat-value">${result.scale_factor.toFixed(2)}x</span>
                                <span class="result-stat-label">Scale</span>
                            </div>
                        </div>
                    </div>
                    <div class="result-actions">
                        <a href="${result.download_url}" class="download-btn" download>
                            <i class="fas fa-download"></i> Download
                        </a>
                    </div>
                </div>
            `;
        }).join('');

        // Show results section
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async downloadAll() {
        const successfulResults = this.processedResults.filter(r => !r.error);
        if (successfulResults.length === 0) {
            this.showError('No files available for download');
            return;
        }

        const filenames = successfulResults.map(r => r.output_filename);

        try {
            const response = await fetch('/download_all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filenames })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'reduced_images.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Error downloading files:', error);
            this.showError(`Error downloading files: ${error.message}`);
        }
    }

    clearAll() {
        this.selectedFiles = [];
        this.processedResults = [];
        this.updateFileList();
        this.updateProcessButton();
        this.hideProgress();
        this.resultsSection.style.display = 'none';
        this.fileInput.value = '';
    }

    showError(message) {
        // Create and show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;

        // Insert after header
        const header = document.querySelector('.header');
        header.insertAdjacentElement('afterend', errorDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);

        // Scroll to error
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    }

    showSuccess(message) {
        // Create and show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;

        // Insert after header
        const header = document.querySelector('.header');
        header.insertAdjacentElement('afterend', successDiv);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ImageReducerApp();
});
