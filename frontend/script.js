let selectedEngine = "v2";

document.getElementById('btnV1').onclick = () => { selectedEngine = "v1"; updateToggleUI('btnV1', 'btnV2'); };
document.getElementById('btnV2').onclick = () => { selectedEngine = "v2"; updateToggleUI('btnV2', 'btnV1'); };

function updateToggleUI(a, b) {
    document.getElementById(a).classList.add('active');
    document.getElementById(b).classList.remove('active');
    document.getElementById('dashboard').style.display = 'none';
}

function formatText(t) {
    return t ? t.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent)">$1</strong>').replace(/^[-\*\d\.\s]+/, '') : "";
}

document.getElementById('fileInput').onchange = function() {
    document.getElementById('fileNameDisplay').innerText = "Selected: " + this.files[0]?.name;
};

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const dashboard = document.getElementById('dashboard');
    const loading = document.getElementById('loading');
    const visualsContainer = document.getElementById('visualsContainer');

    if (fileInput.files.length === 0) return alert("Select file!");

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    document.getElementById('loadingText').innerText = `CRUNCHING DATA WITH ${selectedEngine.toUpperCase()}...`;
    loading.style.display = 'block';
    dashboard.style.display = 'none';

    try {
        const response = await fetch(`http://127.0.0.1:8000/analyze?engine=${selectedEngine}`, {
            method: 'POST', body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            // 1. Fill Stats
            document.getElementById('statRows').innerText = data.basic_info.total_rows.toLocaleString();
            document.getElementById('statCols').innerText = data.basic_info.total_columns;
            document.getElementById('statStatus').innerText = data.cleaning_report.duplicates_removed + " Cleaned";

            // 2. Fill AI Box
            const aiBox = document.getElementById('aiSummaryBox');
            if (data.ai_summary) {
                aiBox.style.display = 'block';
                document.getElementById('aiSummaryText').innerHTML = formatText(data.ai_summary);
            } else { aiBox.style.display = 'none'; }

            // 3. Fill Insights
            const list = document.getElementById('insightsList');
            list.innerHTML = '';
            data.insights.forEach(ins => {
                const li = document.createElement('li');
                li.className = "insight-item";
                li.innerHTML = "💡 " + formatText(ins);
                list.appendChild(li);
            });

            // 4. FIX: DYNAMICALLY BUILD THE CHART CARDS
            visualsContainer.innerHTML = ''; // Wipe anything old
            
            Object.keys(data.visualizations).forEach(key => {
                const chart = data.visualizations[key];
                const title = key.replace(/_/g, ' ').toUpperCase();
                
                // We create the FULL HTML structure for the card here
                const cardHtml = `
                    <div class="card chart-card" style="margin-bottom: 2rem;">
                        <div class="card-header"><h3>📊 ${title}</h3></div>
                        <div class="chart-container" style="background:#000; padding:10px; display:flex; justify-content:center;">
                            <img src="data:image/png;base64,${chart.image}" style="max-width:100%; max-height:350px; object-fit:contain;">
                        </div>
                        <p class="chart-info" style="padding:15px; background:#080808; font-size:0.85rem; color:#888; border-top:1px solid #222;">
                            ${chart.explanation}
                        </p>
                    </div>
                `;
                visualsContainer.insertAdjacentHTML('beforeend', cardHtml);
            });

            // 5. Switch from Skeleton to Dashboard
            loading.style.display = 'none';
            dashboard.style.display = 'grid';
            dashboard.style.opacity = "1";

        } else { alert(data.message); loading.style.display = 'none'; }
    } catch (e) { alert("Server error"); loading.style.display = 'none'; }
}