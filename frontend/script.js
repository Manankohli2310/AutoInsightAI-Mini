// --- CONFIGURATION ---
const API_BASE_URL = "http://127.0.0.1:8000";
let selectedEngine = "v2";
let currentFileId = null; // Stores the ID for downloading cleaned data

// --- ENGINE SELECTION LOGIC ---
document.getElementById('btnV1').onclick = () => { 
    selectedEngine = "v1"; 
    updateToggleUI('btnV1', 'btnV2'); 
};
document.getElementById('btnV2').onclick = () => { 
    selectedEngine = "v2"; 
    updateToggleUI('btnV2', 'btnV1'); 
};

function updateToggleUI(activeId, inactiveId) {
    document.getElementById(activeId).classList.add('active');
    document.getElementById(inactiveId).classList.remove('active');
    // Hide dashboard to force a re-analysis for the new engine
    const dashboard = document.getElementById('dashboard');
    dashboard.style.display = 'none';
}

// --- DATA FORMATTING UTILITY ---
function formatText(t) {
    if (!t) return "";
    // 1. Convert Markdown Bold to HTML Strong
    let cleaned = t.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent)">$1</strong>');
    // 2. Remove leading bullet points or numbers (e.g., "1. ", "- ")
    cleaned = cleaned.replace(/^[-\*\d\.\s]+/, '');
    return cleaned;
}

// --- FILE SELECTION & VALIDATION ---
document.getElementById('fileInput').onchange = function() {
    const file = this.files[0];
    const display = document.getElementById('fileNameDisplay');
    
    if (file) {
        // Validation: Check File Type
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!validTypes.includes(file.type) && !file.name.endsWith('.csv')) {
            alert("Invalid format! Please upload a CSV or Excel file.");
            this.value = "";
            display.innerText = "No file selected";
            return;
        }

        // Validation: Check File Size (Limit: 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert("File too large! Please upload a file smaller than 10MB.");
            this.value = "";
            display.innerText = "No file selected";
            return;
        }

        display.innerHTML = `Selected: <b>${file.name}</b> (${(file.size / 1024).toFixed(1)} KB)`;
    }
};

// --- DOWNLOAD FEATURE ---
async function downloadCleanedData() {
    if (!currentFileId) return alert("No cleaned data available.");
    // Directly trigger the FastAPI download endpoint
    window.location.href = `${API_BASE_URL}/download/${currentFileId}`;
}

// --- CORE ANALYSIS EXECUTION ---
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const dashboard = document.getElementById('dashboard');
    const loading = document.getElementById('loading');
    const list = document.getElementById('insightsList');
    const visualsContainer = document.getElementById('visualsContainer');

    if (fileInput.files.length === 0) return alert("Please select a dataset to analyze!");

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Show Loading State
    document.getElementById('loadingText').innerText = `CRUNCHING DATA WITH ${selectedEngine.toUpperCase()}...`;
    loading.style.display = 'block';
    dashboard.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/analyze?engine=${selectedEngine}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Store file_id for the download button
            currentFileId = data.file_id;

            // 1. Populate Summary Stats
            document.getElementById('statRows').innerText = data.basic_info.total_rows.toLocaleString();
            document.getElementById('statCols').innerText = data.basic_info.total_columns;
            
            // Detailed health status (how many columns were dropped + dupes)
            const dropped = data.cleaning_report.dropped_columns.length;
            document.getElementById('statStatus').innerText = `${dropped} Noise Columns Dropped`;

            // 2. Handle AI Executive Summary (V2 only)
            const aiBox = document.getElementById('aiSummaryBox');
            if (data.ai_summary) {
                aiBox.style.display = 'block';
                document.getElementById('aiSummaryText').innerHTML = formatText(data.ai_summary);
            } else {
                aiBox.style.display = 'none';
            }

            // 3. Populate Insights List
            list.innerHTML = '';
            data.insights.forEach(ins => {
                if (ins.length > 5) { // Skip empty/garbage lines
                    const li = document.createElement('li');
                    li.className = "insight-item";
                    li.innerHTML = "💡 " + formatText(ins);
                    list.appendChild(li);
                }
            });

            // 4. DYNAMIC VISUALS: Build cards based on "Interestingness"
            visualsContainer.innerHTML = ''; // Wipe old containers
            
            const vKeys = Object.keys(data.visualizations);
            if (vKeys.length === 0) {
                visualsContainer.innerHTML = '<div class="card" style="padding:30px; text-align:center; color:#888;">No statistically significant visuals found for this specific dataset.</div>';
            } else {
                vKeys.forEach(key => {
                    const chart = data.visualizations[key];
                    const cleanTitle = key.replace(/_/g, ' ').toUpperCase();
                    
                    const cardHtml = `
                        <div class="card chart-card" style="margin-bottom: 2.5rem; border: 1px solid #222;">
                            <div class="card-header"><h3 style="color:var(--accent)">📊 ${cleanTitle}</h3></div>
                            <div class="chart-container" style="background:#000; padding:15px; display:flex; justify-content:center;">
                                <img src="data:image/png;base64,${chart.image}" style="max-width:100%; max-height:380px; object-fit:contain;">
                            </div>
                            <p class="chart-info" style="padding:15px; background:#080808; font-size:0.85rem; color:#aaa; line-height:1.6; border-top:1px solid #222;">
                                <b>Interpretation:</b> ${chart.explanation}
                            </p>
                        </div>
                    `;
                    visualsContainer.insertAdjacentHTML('beforeend', cardHtml);
                });
            }

            // 5. Add Download Button to the UI (One-time check)
            if (!document.getElementById('downloadBtn')) {
                const btnHtml = `<button id="downloadBtn" class="analyze-btn" onclick="downloadCleanedData()" style="background:var(--accent); color:#000; margin-top:20px;">📥 Download Cleaned Dataset</button>`;
                document.querySelector('.upload-area .drop-zone').insertAdjacentHTML('beforeend', btnHtml);
            }

            // 6. Reveal Dashboard with Transition
            loading.style.display = 'none';
            dashboard.style.display = 'grid';
            dashboard.style.opacity = "0";
            setTimeout(() => {
                dashboard.style.transition = "opacity 0.8s ease-in";
                dashboard.style.opacity = "1";
                dashboard.scrollIntoView({ behavior: 'smooth' });
            }, 50);

        } else {
            alert(`Analysis Error: ${data.message}`);
            loading.style.display = 'none';
        }
    } catch (e) {
        console.error("Critical Connection Error:", e);
        alert("Server is offline or unreachable. Please ensure the FastAPI backend is running.");
        loading.style.display = 'none';
    }
}