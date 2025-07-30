const summarizeBtn = document.getElementById("summarizeBtn");
const videoUrlInput = document.getElementById("videoUrl");
const summaryText = document.getElementById("summaryText");
const resultDiv = document.getElementById("result");

// Change this to your backend API (use ngrok/public URL when sharing)
const API_URL = "http://127.0.0.1:8000/summarize";

summarizeBtn.addEventListener("click", async () => {
    const videoUrl = videoUrlInput.value.trim();
    if (!videoUrl) {
        alert("Please enter a YouTube URL.");
        return;
    }

    summaryText.innerText = "Loading...";
    resultDiv.style.display = "block";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ url: videoUrl }),
        });

        const data = await response.json();
        summaryText.innerText = JSON.stringify(data.summary, null, 2);
    } catch (error) {
        summaryText.innerText = "Error: " + error;
    }
});
