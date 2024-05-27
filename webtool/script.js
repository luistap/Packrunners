document.addEventListener("DOMContentLoaded", function() {
    let canvas = document.getElementById('canvas');
    let ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';  // Set high-quality image smoothing

    let rectangles = [];
    let currentRect = null;
    let drag = false;
    let imageLoaded = false;
    let image = new Image();

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

        if (imageLoaded) {
            ctx.strokeStyle = "red";  // Visible color for the rectangle borders
            ctx.lineWidth = 2;

            rectangles.forEach(rect => {
                ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
            });

            if (currentRect) {
                ctx.strokeRect(currentRect.startX, currentRect.startY, currentRect.w, currentRect.h);
            }

            ctx.globalAlpha = 0.2;  // Lower opacity for filled rectangles
            ctx.fillStyle = "gray";
            ctx.globalCompositeOperation = 'multiply';

            rectangles.forEach(rect => {
                ctx.fillRect(rect.startX, rect.startY, rect.w, rect.h);
            });

            if (currentRect) {
                ctx.fillRect(currentRect.startX, currentRect.startY, currentRect.w, currentRect.h);
            }

            ctx.globalAlpha = 1.0;
            ctx.globalCompositeOperation = 'source-over';  // Reset blend mode
        }
    }

    document.getElementById('upload').addEventListener('change', function(e) {
        const reader = new FileReader();
        reader.onload = function(event) {
            image.onload = function() {
                canvas.width = image.width;
                canvas.height = image.height;
                imageLoaded = true;
                rectangles = [];
                console.log("Image loaded and rectangles array cleared.");
                draw();
            };
            image.src = event.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
    });

    canvas.addEventListener('mousedown', function(e) {
        currentRect = {
            startX: e.pageX - canvas.offsetLeft,
            startY: e.pageY - canvas.offsetTop,
            w: 0,
            h: 0
        };
        drag = true;
    });

    canvas.addEventListener('mouseup', function() {
        if (currentRect && currentRect.w !== 0 && currentRect.h !== 0) {
            rectangles.push(currentRect);
            console.log(`Rectangle added: (${currentRect.startX}, ${currentRect.startY}, ${currentRect.w}, ${currentRect.h})`);
        }
        currentRect = null;
        drag = false;
        draw();
    });

    canvas.addEventListener('mousemove', function(e) {
        if (drag && imageLoaded && currentRect) {
            currentRect.w = (e.pageX - canvas.offsetLeft) - currentRect.startX;
            currentRect.h = (e.pageY - canvas.offsetTop) - currentRect.startY;
            draw();
        }
    });

    document.getElementById('submit').addEventListener('click', async function() {
        console.log(`Attempting to submit with ${rectangles.length} rectangles.`);
        if (rectangles.length !== 4) {
            alert('Please draw exactly four rectangles before submitting.');
            return;
        }

        const formData = new FormData();
        const labels = ['team1_names', 'team2_names', 'team1_stats', 'team2_stats'];
        let blobPromises = labels.map((label, index) => {
            return new Promise(resolve => {
                if (index < rectangles.length) {
                    const rect = rectangles[index];
                    const blobCanvas = document.createElement('canvas');
                    blobCanvas.width = rect.w;
                    blobCanvas.height = rect.h;
                    const blobCtx = blobCanvas.getContext('2d');
                    blobCtx.drawImage(canvas, rect.startX, rect.startY, rect.w, rect.h, 0, 0, rect.w, rect.h);
                    blobCanvas.toBlob(blob => {
                        if (blob) {
                            console.log(`Blob created for ${label}, size: ${blob.size} bytes`);
                            formData.append(label, blob, `section${index}.png`);
                        } else {
                            console.log(`Failed to create blob for ${label}`);
                            formData.append(label, new Blob(), `empty_${index}.png`);
                        }
                        resolve();
                    }, 'image/png');
                } else {
                    formData.append(label, new Blob(), `empty_${index}.png`);
                    resolve();
                }
            });
        });

        await Promise.all(blobPromises);

        // append the rest of the values

        const map = document.getElementById('map-select').value;
        const match_type = document.getElementById('match-type-select').value;
        const scoreTeam1 = document.getElementById('score-team1').value;
        const scoreTeam2 = document.getElementById('score-team2').value;

        if (!map || !match_type || scoreTeam1 === '' || scoreTeam2 === '') {
            alert('Please fill in all fields before submitting.');
            return;
        }

        const final_score = `${scoreTeam1}-${scoreTeam2}`;
        formData.append('map', map);
        formData.append('match_type', match_type)
        formData.append('final_score', final_score);
        console.log('All blobs added to formData');
        submitImage(formData);
    });

    async function submitImage(formData) {
        console.log('Attempting to submit to backend');
        try {
            const response = await fetch('http://127.0.0.1:8000/upload/', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                console.log('Images successfully submitted!');
                const result = await response.json();
                console.log(result);
                alert('Images processed: ' + result.message);
            } else {
                console.error('Failed to submit images:', response.statusText);
                alert('Error processing images: ' + response.statusText);
            }
        } catch (error) {
            console.error('Error submitting images:', error);
            alert('Network or server error.');
        }
    }
});
