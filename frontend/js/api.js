// --- Configuration ---
// Uncomment the appropriate line for your environment
// const BACKEND_URL = 'http://127.0.0.1:8000'; // Local
const BACKEND_URL = 'https://secure-notes-share.onrender.com'; // Production

const API_BASE = `${BACKEND_URL}/api`;

async function fetchBatches() {
    const response = await fetch(`${API_BASE}/batches/`);
    return await response.json();
}

async function createBatch(name) {
    const response = await fetch(`${API_BASE}/batches/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
    });
    return await response.json();
}

async function getBatch(id) {
    const response = await fetch(`${API_BASE}/batches/${id}`);
    if (!response.ok) {
        throw new Error('Batch not found');
    }
    return await response.json();
}

async function addStudent(batchId, name, phone) {
    const response = await fetch(`${API_BASE}/batches/${batchId}/students/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phone }),
    });
    return await response.json();
}

async function uploadPdf(batchId, file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/batches/${batchId}/upload_pdf`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Upload failed');
    }

    return await response.json();
}

function sendToWhatsApp(phone, name, pdfUrl) {
    // Construct the full URL.
    // Verify if pdfUrl already has http. If not, prepend BACKEND_URL.
    let fullPdfUrl = pdfUrl;
    if (!pdfUrl.startsWith('http')) {
        fullPdfUrl = BACKEND_URL + pdfUrl;
    }

    // Sanitize phone: remove non-numeric characters
    const safePhone = phone.replace(/\D/g, '');

    const message = fullPdfUrl;
    const encodedMessage = encodeURIComponent(message);

    // The WhatsApp Deep Link
    const waLink = `https://wa.me/${safePhone}?text=${encodedMessage}`;

    // Open in a new tab
    window.open(waLink, '_blank');
}
