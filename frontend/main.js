document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const executeButton = document.getElementById('executeButton');
    const fileName = document.getElementById('fileName');
    const loadingSection = document.querySelector('.loading-section');
    const resultsSection = document.querySelector('.results-section');
    const resultsTableBody = document.getElementById('resultsTableBody');
    const fileInputWrapper = document.querySelector('.file-input-wrapper');
    const progressFill = document.querySelector('.progress-fill');

    // Animacija za hero sekciju
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.style.opacity = '0';
        heroTitle.style.transform = 'translateY(20px)';
        setTimeout(() => {
            heroTitle.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
            heroTitle.style.opacity = '1';
            heroTitle.style.transform = 'translateY(0)';
        }, 100);
    }

    // Drag and drop funkcionalnost
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileInputWrapper.classList.add('highlight');
    }

    function unhighlight(e) {
        fileInputWrapper.classList.remove('highlight');
    }

    fileInputWrapper.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFile(file);
    }

    function handleFile(file) {
        if (file) {
            if (file.name.endsWith('.mp3') || file.name.endsWith('.mp4')) {
                executeButton.disabled = false;
                fileName.textContent = `Izabran fajl: ${file.name}`;
                fileInput.files = new DataTransfer().files;
            } else {
                alert('Molimo izaberite MP3 ili MP4 fajl.');
                executeButton.disabled = true;
                fileName.textContent = '';
            }
        }
    }

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        handleFile(file);
    });

    executeButton.addEventListener('click', async function() {
        const file = fileInput.files[0];
        if (!file) return;

        document.querySelector('.upload-section').style.display = 'none';
        loadingSection.style.display = 'block';
        resultsSection.style.display = 'none';

        // Simulacija progresa
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 1;
            progressFill.style.width = `${progress}%`;
            if (progress >= 100) {
                clearInterval(progressInterval);
                
                // Primer podataka
                const results = [
                    { pitanje: "Prvo pitanje?", odgovor: "Prvi odgovor" },
                    { pitanje: "Drugo pitanje?", odgovor: "Drugi odgovor" }
                ];

                resultsTableBody.innerHTML = '';
                results.forEach(result => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${result.pitanje}</td>
                        <td>${result.odgovor}</td>
                    `;
                    resultsTableBody.appendChild(row);
                });

                setTimeout(() => {
                    loadingSection.style.display = 'none';
                    resultsSection.style.display = 'block';
                }, 500);
            }
        }, 30);
    });
});
