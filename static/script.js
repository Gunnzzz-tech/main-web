// Toast notification function
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// File upload handler
const fileInput = document.getElementById('cv');
const fileLabel = document.getElementById('fileLabel');
const fileNameSpan = document.getElementById('fileName');

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        fileNameSpan.textContent = file.name;
        fileLabel.classList.add('has-file');
        lucide.createIcons();
    }
});

// Form reset handler
const resetBtn = document.getElementById('resetBtn');
const jobForm = document.getElementById('jobForm');

resetBtn.addEventListener('click', function() {
    jobForm.reset();
    fileNameSpan.textContent = 'Click to upload your resume (PDF, DOC, DOCX)';
    fileLabel.classList.remove('has-file');
    showToast('Form cleared', 'info');
    lucide.createIcons();

    // ✅ Optional GA tracking
    if (typeof gtag === 'function') {
        gtag('event', 'form_reset', {
            'event_category': 'Form',
            'event_label': 'Application Form Reset'
        });
    }
});

// ✅ Simple submit (redirect handled by Flask)
jobForm.addEventListener('submit', () => {
    if (typeof gtag === 'function') {
        gtag('event', 'form_submission', {
            'event_category': 'Form',
            'event_label': 'Application Submitted'
        });
    }
});

