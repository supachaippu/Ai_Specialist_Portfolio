document.addEventListener('DOMContentLoaded', async () => {
    try {
        await liff.init({ liffId: 'YOUR_LIFF_ID_HERE' });
        if (liff.isLoggedIn() || liff.isInClient()) {
            const profile = await liff.getProfile();
            const userId = profile.userId;
            console.log('Logged in as:', userId);
            
            // Auto-load latest transactions from D1
            loadLatestData(userId);
        } else {
            console.log('LIFF initialized (External Browser)');
        }
    } catch (err) {
        console.error('LIFF Init Error:', err);
    }
});

async function loadLatestData(userId) {
    try {
        const response = await fetch(`${API_URL}/api/get-latest-transactions?userId=${userId}`);
        const result = await response.json();
        if (result.transactions && result.transactions.length > 0) {
            currentTransactions = result.transactions;
            renderDashboard();
            uploadSection.classList.replace('active-view', 'hidden-view');
            dashboardSection.classList.replace('hidden-view', 'active-view');
        }
    } catch (e) {
        console.error('Error loading latest data:', e);
    }
}

// DOM Elements
const fileDropArea = document.getElementById('file-drop-area');
const fileInput = document.getElementById('pdf-file');
const fileNameDisplay = document.getElementById('file-name-display');
const uploadForm = document.getElementById('upload-form');
const loadingSpinner = document.getElementById('loading-spinner');
const submitBtn = document.getElementById('submit-btn');

const uploadSection = document.getElementById('upload-section');
const dashboardSection = document.getElementById('dashboard-section');
const detailSection = document.getElementById('detail-section');
const btnBackUpload = document.getElementById('btn-back-upload');
const btnBackDashboard = document.getElementById('btn-back-dashboard');

const AVAILABLE_TAGS = ['อาหาร/ของใช้', 'เดินทาง/เติมเงิน', 'ช้อปปิ้ง', 'ค่าใช้จ่าย/บิล', 'ยอดขาย (แม่มณี)', 'รับเงินโอน', 'โอนเงินออก', 'อื่นๆ'];
const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#64748b', '#ef4444', '#14b8a6'];

let currentTransactions = [];
let expenseChartInstance = null;

// File Upload Interactions
fileDropArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = fileInput.files[0].name;
        fileNameDisplay.style.color = 'var(--primary)';
    }
});

// --- API Configuration ---
const API_URL = 'https://YOUR_WORKER_SUBDOMAIN.workers.dev';
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

async function extractTextFromPDF(file, password) {
    const arrayBuffer = await file.arrayBuffer();
    const loadingTask = pdfjsLib.getDocument({
        data: arrayBuffer,
        password: password
    });
    const pdf = await loadingTask.promise;
    let fullText = "";
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(" ");
        fullText += pageText + "\n";
    }
    return fullText;
}

// Form Submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (fileInput.files.length === 0) return alert('กรุณาเลือกไฟล์ PDF');

    const file = fileInput.files[0];
    const password = document.getElementById('pdf-password').value;

    submitBtn.classList.add('hidden-view');
    loadingSpinner.classList.remove('hidden');
    loadingSpinner.style.display = 'block';

    try {
        // 1. Extract Text locally (Fast!)
        const extractedText = await extractTextFromPDF(file, password);
        
        // 2. Send to Cloudflare Worker (Wait for response)
        const response = await fetch(`${API_URL}/api/parse-statement`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: extractedText })
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'เกิดข้อผิดพลาดในการเชื่อมต่อ');

        // 3. Show Result immediately on Dashboard
        currentTransactions = result.transactions;
        const insights = result.insights || "วิเคราะห์ข้อมูลเรียบร้อยแล้ว";
        document.getElementById('ai-insights-text').innerText = insights;
        
        renderDashboard();
        
        uploadSection.classList.replace('active-view', 'hidden-view');
        dashboardSection.classList.replace('hidden-view', 'active-view');

    } catch (error) {
        alert("เกิดข้อผิดพลาด: " + error.message);
        console.error(error);
        submitBtn.classList.remove('hidden-view');
    } finally {
        loadingSpinner.style.display = 'none';
        loadingSpinner.classList.add('hidden');
    }
});

// Navigation Back
btnBackUpload.addEventListener('click', () => {
    dashboardSection.classList.replace('active-view', 'hidden-view');
    uploadSection.classList.replace('hidden-view', 'active-view');
});

btnBackDashboard.addEventListener('click', () => {
    detailSection.classList.replace('active-view', 'hidden-view');
    dashboardSection.classList.replace('hidden-view', 'active-view');
    // Re-render dashboard to reflect any tag changes
    renderDashboard();
});

// --- RENDER LOGIC ---

function renderDashboard() {
    let totalIncome = 0;
    let totalExpense = 0;
    const categoryTotals = {};
    const categoryCounts = {};

    currentTransactions.forEach(tx => {
        if (tx.amount > 0) {
            totalIncome += tx.amount;
        } else {
            totalExpense += Math.abs(tx.amount);
        }
        
        // Count everything (Income and Expense) into categories
        const amt = Math.abs(tx.amount);
        categoryTotals[tx.tag] = (categoryTotals[tx.tag] || 0) + amt;
        categoryCounts[tx.tag] = (categoryCounts[tx.tag] || 0) + 1;
    });

    // Summary Cards
    document.getElementById('total-income').textContent = `฿${totalIncome.toLocaleString('th-TH', {minimumFractionDigits: 2})}`;
    document.getElementById('total-expense').textContent = `฿${totalExpense.toLocaleString('th-TH', {minimumFractionDigits: 2})}`;

    renderChart(categoryTotals);
    renderCategoryCards(categoryTotals, categoryCounts);
}

function renderChart(categoryTotals) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    if (expenseChartInstance) expenseChartInstance.destroy();

    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);

    expenseChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: CHART_COLORS,
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            cutout: '75%'
        }
    });
}

function renderCategoryCards(categoryTotals, categoryCounts) {
    const listContainer = document.getElementById('category-cards-list');
    listContainer.innerHTML = '';

    const labels = Object.keys(categoryTotals);
    
    labels.forEach((label, i) => {
        const color = CHART_COLORS[i % CHART_COLORS.length];
        const amount = categoryTotals[label];
        const count = categoryCounts[label];
        
        // Determine if it's mostly income or expense to color text
        // (Simplified logic: "รับเงินโอน", "ยอดขาย" are income)
        const isIncome = label.includes('รับ') || label.includes('ยอดขาย');
        const amountClass = isIncome ? 'text-success' : 'text-danger';
        const sign = isIncome ? '+' : '-';

        const card = document.createElement('div');
        card.className = 'cat-card';
        card.onclick = () => openCategoryDetail(label);
        
        card.innerHTML = `
            <div class="cat-card-header">
                <div class="cat-card-color" style="background-color: ${color}"></div>
                <div class="cat-card-count">${count} รายการ</div>
            </div>
            <div class="cat-card-info">
                <h4>${label}</h4>
                <div class="cat-card-amount ${amountClass}">
                    ${sign}฿${amount.toLocaleString('th-TH', {minimumFractionDigits: 2})}
                </div>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

// --- BULK TAGGING LOGIC ---

// --- BULK TAGGING LOGIC (Flashcard UX) ---

let currentDetailTag = '';
let currentDetailQueue = [];
let currentDetailGroupKey = '';

function openCategoryDetail(tag) {
    currentDetailTag = tag;
    // 1. Switch View
    dashboardSection.classList.replace('active-view', 'hidden-view');
    detailSection.classList.replace('hidden-view', 'active-view');
    
    // 2. Set Title with Edit Button
    document.getElementById('detail-category-title').innerHTML = `
        หมวด: ${tag} <i class="ph ph-pencil-simple" style="font-size:1rem; cursor:pointer; color:var(--primary)" onclick="editCategoryName('${tag}')"></i>
    `;
    
    // 3. Filter and Group Data
    const filteredTx = currentTransactions.filter(tx => tx.tag === tag);
    const groupedDesc = {};
    
    filteredTx.forEach(tx => {
        // Use group_name from AI if available, otherwise fallback to description
        const groupKey = tx.group_name || tx.description;
        if (!groupedDesc[groupKey]) {
            groupedDesc[groupKey] = { count: 0, amount: 0, type: tx.type, raw_descriptions: new Set() };
        }
        groupedDesc[groupKey].count++;
        groupedDesc[groupKey].amount += Math.abs(tx.amount);
        groupedDesc[groupKey].raw_descriptions.add(tx.description);
    });
    
    // Convert to array for queue
    currentDetailQueue = Object.keys(groupedDesc).map(k => ({ key: k, ...groupedDesc[k] }));
    
    // Render the first item in queue
    renderQueueCard();
}

function renderQueueCard() {
    const container = document.getElementById('bulk-list');
    if (currentDetailQueue.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding: 40px 20px;">
                <i class="ph ph-check-circle" style="font-size: 4rem; color: var(--success);"></i>
                <h3 class="mt-3">จัดการครบแล้ว!</h3>
                <p style="color: var(--text-muted); font-size:0.85rem; margin-top:10px;">คุณเคลียร์รายการในหมวดหมู่นี้หมดแล้ว</p>
                <button class="btn-primary mt-4 w-100" onclick="document.getElementById('btn-back-dashboard').click()">กลับไปหน้าหลัก</button>
            </div>
        `;
        return;
    }
    
    const item = currentDetailQueue[0];
    currentDetailGroupKey = item.key;
    const amountText = `฿${item.amount.toLocaleString('th-TH', {minimumFractionDigits: 2})}`;
    
    // Tags to choose from
    let allTags = [...new Set([...AVAILABLE_TAGS, ...currentTransactions.map(t=>t.tag)])];
    
    const tagOptions = allTags.map(t => 
        `<button class="tag-chip ${t === currentDetailTag ? 'active' : ''}" onclick="tagQueueItem('${t}')">${t}</button>`
    ).join('');

    container.innerHTML = `
        <div class="bulk-item" style="display:block; padding: 25px 20px;">
            <div style="display:flex; justify-content:center; margin-bottom:15px;">
                <span style="background:rgba(255,255,255,0.1); padding:4px 12px; border-radius:20px; font-size:0.75rem;">
                    คิวที่ 1 จาก ${currentDetailQueue.length}
                </span>
            </div>
            
            <h2 style="text-align:center; margin-bottom: 10px; font-weight: 500;">${item.key}</h2>
            
            <div style="text-align:center; margin-bottom: 20px;">
                <div class="${item.amount > 0 ? 'text-success' : 'text-danger'} font-bold" style="font-size:1.8rem;">
                    ${item.amount > 0 ? '+' : '-'}${amountText}
                </div>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top:5px;">(รวมจาก ${item.count} รายการ)</div>
            </div>
            
            <p style="font-size: 0.75rem; color: rgba(255,255,255,0.4); text-align:center; margin-bottom: 25px;">
                ตัวอย่างคำบรรยาย: ${Array.from(item.raw_descriptions).slice(0, 2).join(', ')}
            </p>
            
            <h4 style="text-align:center; margin-bottom:12px; font-size:0.9rem; font-weight:400; color:var(--text-main);">ย้ายไปหมวดหมู่ไหนดี?</h4>
            <div class="quick-tags-grid">
                ${tagOptions}
            </div>
            
            <div style="margin-top: 25px;">
                <button class="btn-secondary w-100" onclick="skipQueueItem()"><i class="ph ph-skip-forward"></i> ข้ามรายการนี้ไปก่อน</button>
            </div>
        </div>
    `;
}

window.tagQueueItem = function(newTag) {
    if (!currentDetailGroupKey) return;
    
    // Update data
    let updatedCount = 0;
    currentTransactions.forEach(tx => {
        const txKey = tx.group_name || tx.description;
        if (txKey === currentDetailGroupKey) {
            tx.tag = newTag;
            updatedCount++;
        }
    });
    console.log(`Updated ${updatedCount} transactions to tag: ${newTag}`);
    
    // Remove from queue and render next
    currentDetailQueue.shift();
    renderQueueCard();
};

window.skipQueueItem = function() {
    // Move current item to the back of the queue
    const item = currentDetailQueue.shift();
    currentDetailQueue.push(item);
    renderQueueCard();
};

window.saveToDatabase = async function() {
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> กำลังบันทึก...';
    btn.disabled = true;

    try {
        let userId = null;
        if (liff.isLoggedIn() || liff.isInClient()) {
            const profile = await liff.getProfile();
            userId = profile.userId;
        }

        const response = await fetch(`${API_URL}/api/save-transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transactions: currentTransactions, userId: userId })
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'เกิดข้อผิดพลาดในการบันทึก');
        
        // 1. Calculate totals for Flex Message
        let totalInc = 0, totalExp = 0;
        const catTotals = {};
        currentTransactions.forEach(tx => {
            if (tx.amount > 0) totalInc += tx.amount;
            else totalExp += Math.abs(tx.amount);
            catTotals[tx.tag] = (catTotals[tx.tag] || 0) + Math.abs(tx.amount);
        });
        
        // Find top 3 categories
        const topCats = Object.entries(catTotals)
            .sort((a,b) => b[1] - a[1])
            .slice(0, 3);
            
        const topCatContents = topCats.map(([tag, amt]) => ({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                { "type": "text", "text": `• ${tag}`, "color": "#aaaaaa", "flex": 2, "size": "sm" },
                { "type": "text", "text": `฿${amt.toLocaleString('th-TH', {minimumFractionDigits: 2})}`, "align": "end", "color": "#ffffff", "flex": 1, "size": "sm" }
            ],
            "margin": "sm"
        }));

        // 2. Construct Flex Message
        const flexMsg = {
            "type": "flex",
            "altText": "สรุปรายการบัญชีประจำเดือน",
            "contents": {
              "type": "bubble",
              "size": "mega",
              "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  { "type": "text", "text": "📊 สรุปรายการบัญชี", "weight": "bold", "size": "xl", "color": "#ffffff" }
                ],
                "backgroundColor": "#1e293b"
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      { "type": "text", "text": "รายรับรวม", "color": "#888888" },
                      { "type": "text", "text": `+฿${totalInc.toLocaleString('th-TH', {minimumFractionDigits: 2})}`, "align": "end", "color": "#10b981", "weight": "bold" }
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      { "type": "text", "text": "รายจ่ายรวม", "color": "#888888" },
                      { "type": "text", "text": `-฿${totalExp.toLocaleString('th-TH', {minimumFractionDigits: 2})}`, "align": "end", "color": "#ef4444", "weight": "bold" }
                    ],
                    "margin": "md"
                  },
                  { "type": "separator", "margin": "lg", "color": "#334155" },
                  { "type": "text", "text": "🔥 รายจ่ายยอดฮิต", "weight": "bold", "margin": "lg", "color": "#ffffff", "size": "sm" },
                  ...topCatContents
                ],
                "backgroundColor": "#0f172a"
              }
            }
        };

        // 3. Send Message and Close
        if (liff.isLoggedIn() && liff.isInClient()) {
            await liff.sendMessages([flexMsg]);
            alert('บันทึกและส่งรายงานเรียบร้อย!');
            liff.closeWindow();
        } else {
            alert(result.message + "\n\n(ระบบได้จำลองการส่ง Flex Message แล้ว แต่คุณไม่ได้เปิดผ่านแอป LINE)");
            console.log("Flex Message Payload:", flexMsg);
        }

    } catch (error) {
        alert(error.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
};
