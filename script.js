document.addEventListener('DOMContentLoaded', () => {
    const uploadM5Button = document.getElementById('upload-m5');
    const uploadM15Button = document.getElementById('upload-m15');
    const fileInputM5 = document.getElementById('file-input-m5');
    const fileInputM15 = document.getElementById('file-input-m15');
    const analyzeButton = document.getElementById('analyze-button');
    const canvasM5 = document.getElementById('canvas-m5');
    const canvasM15 = document.getElementById('canvas-m15');
    const resultDisplay = document.getElementById('result-display');
    let imageDataM5 = null;
    let imageDataM15 = null;
    const handleImageUpload = (file, canvasElement, dataStore) => {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasElement.getContext('2d');
                    canvasElement.width = img.width;
                    canvasElement.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    canvasElement.style.display = 'block';
                    if (dataStore === 'm5') imageDataM5 = canvasElement.toDataURL('image/jpeg', 0.9);
                    if (dataStore === 'm15') imageDataM15 = canvasElement.toDataURL('image/jpeg', 0.9);
                    checkIfReadyToAnalyze();
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    };
    uploadM5Button.addEventListener('click', () => fileInputM5.click());
    uploadM15Button.addEventListener('click', () => fileInputM15.click());
    fileInputM5.addEventListener('change', (e) => handleImageUpload(e.target.files[0], canvasM5, 'm5'));
    fileInputM15.addEventListener('change', (e) => handleImageUpload(e.target.files[0], canvasM15, 'm15'));
    const checkIfReadyToAnalyze = () => {
        if (imageDataM5 && imageDataM15) {
            analyzeButton.disabled = false;
            resultDisplay.innerHTML = '<p>الصور جاهزة للتحليل. اضغط "حلّل الآن".</p>';
        }
    };
    analyzeButton.addEventListener('click', async () => {
        if (!imageDataM5 || !imageDataM15) { return; }
        resultDisplay.innerHTML = '<p>جاري التحليل... قد يستغرق هذا بعض الوقت.</p>';
        analyzeButton.disabled = true;
        try {
            // !!! هام: سنقوم بتغيير هذا الرابط لاحقًا
            const response = await fetch('YOUR_BACKEND_URL/analyze-dual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_m5: imageDataM5, image_m15: imageDataM15 }),
            });
            if (!response.ok) { throw new Error(`Error: ${response.statusText}`); }
            const result = await response.json();
            if (result.prediction) {
                resultDisplay.innerHTML = `<p>التوقع: <span style="color: ${result.prediction === 'صعود' ? '#4CAF50' : '#f44336'}; font-size: 22px;">${result.prediction}</span></p>`;
            } else {
                resultDisplay.innerHTML = `<p>فشل التحليل. حاول مرة أخرى.</p>`;
            }
        } catch (error) {
            console.error("Error:", error);
            resultDisplay.innerHTML = `<p>فشل الاتصال بالخادم. تأكد من الرابط وحاول مرة أخرى.</p>`;
        } finally {
            if (resultDisplay.innerText.includes("فشل")) { analyzeButton.disabled = false; }
        }
    });
});
