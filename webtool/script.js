document.addEventListener("DOMContentLoaded", function() {
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get('image');

    let rectangles = [];
    let drag = false;
    let currentRect = null;

    function drawImageOnCanvas(imgUrl) {
        const image = new Image();

        // Handle CORS
        image.crossOrigin = "Anonymous"; 

        image.onload = function() {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
            console.log("Image loaded and drawn on canvas.");
        };

        image.onerror = function() {
            console.error("Failed to load image.");
        };

        image.src = imgUrl;
    }

    if (imageUrl) {
        drawImageOnCanvas(imageUrl);
    } else {
        console.error("No image URL provided.");
    }

    // Event listeners for canvas drawing
    canvas.addEventListener('mousedown', function(e) {
        currentRect = {
            startX: e.pageX - canvas.offsetLeft,
            startY: e.pageY - canvas.offsetTop,
            w: 0,
            h: 0
        };
        drag = true;
    });

    canvas.addEventListener('mousemove', function(e) {
        if (drag) {
            currentRect.w = (e.pageX - canvas.offsetLeft) - currentRect.startX;
            currentRect.h = (e.pageY - canvas.offsetTop) - currentRect.startY;
            ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear the canvas
            ctx.drawImage(image, 0, 0, canvas.width, canvas.height);  // Redraw the image
            ctx.strokeStyle = "red";
            ctx.strokeRect(currentRect.startX, currentRect.startY, currentRect.w, currentRect.h);
        }
    });

    canvas.addEventListener('mouseup', function() {
        if (currentRect) {
            rectangles.push(currentRect);
            console.log("Rectangle added:", currentRect);
            drag = false;
            currentRect = null;
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
