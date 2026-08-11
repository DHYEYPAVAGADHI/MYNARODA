/*
 * Student Portal — Upload, Preview, Mobile Validation, Form Submission
 * Completely rewritten from scratch for maximum browser compatibility.
 */
document.addEventListener('DOMContentLoaded', function () {

    // ── 1. ELEMENT REFERENCES ────────────────────────────────────────────────
    var dropZone          = document.getElementById('dropZone');
    var workFile          = document.getElementById('workFile');
    var previewContainer  = document.getElementById('workPreviewContainer');
    var imageWrapper      = document.getElementById('imagePreviewWrapper');
    var pdfWrapper        = document.getElementById('pdfPreviewWrapper');
    var previewImage      = document.getElementById('previewImage');
    var selectedFileName  = document.getElementById('selectedFileName');
    var pdfFileName       = document.getElementById('pdfFileName');
    var removeBtn         = document.getElementById('removeWorkFile');
    var studentPhotoInput = document.getElementById('studentPhotoInput');
    var studentPhotoName  = document.getElementById('studentPhotoName');
    var mobileInput       = document.getElementById('guardian_mobile');
    var mobileOk          = document.getElementById('mobile-ok');
    var mobileError       = document.getElementById('mobile-error');
    var mobileLoading     = document.getElementById('mobile-loading');
    var mobileStatusIcon  = document.getElementById('mobile-status-icon');
    var mobileErrorMsg    = document.getElementById('mobile-error-msg');
    var submitBtn         = document.getElementById('student-submit-btn');
    var form              = document.getElementById('studentForm');
    var currentObjectURL  = null;
    var checkTimeout;

    // ── 2. HELPER FUNCTIONS ──────────────────────────────────────────────────
    function formatSize(bytes) {
        var mb = bytes / (1024 * 1024);
        return mb >= 1 ? mb.toFixed(1) + ' MB' : Math.round(bytes / 1024) + ' KB';
    }

    function getCookie(name) {
        var value = '; ' + document.cookie;
        var parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }

    // ── 3. FILE PREVIEW ──────────────────────────────────────────────────────
    function showPreview(file) {
        if (!file) return;

        var ext  = file.name.split('.').pop().toLowerCase();
        var type = file.type;

        var validExts  = ['jpg', 'jpeg', 'png', 'pdf'];
        var validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];

        if (validExts.indexOf(ext) === -1 && validTypes.indexOf(type) === -1) {
            alert('Only JPG, PNG, and PDF files are allowed.');
            workFile.value = '';
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10 MB.');
            workFile.value = '';
            return;
        }

        // Show file name
        if (selectedFileName) {
            selectedFileName.textContent = file.name + ' — ' + formatSize(file.size);
        }

        // Show preview container
        if (previewContainer) previewContainer.classList.remove('hidden');

        // Revoke previous object URL
        if (currentObjectURL) {
            URL.revokeObjectURL(currentObjectURL);
            currentObjectURL = null;
        }

        var isImage = (type.indexOf('image') === 0) || (ext === 'jpg' || ext === 'jpeg' || ext === 'png');

        if (isImage) {
            currentObjectURL = URL.createObjectURL(file);
            if (previewImage) {
                previewImage.src = currentObjectURL;
                previewImage.style.display = 'block';
            }
            if (imageWrapper) imageWrapper.classList.remove('hidden');
            if (pdfWrapper)   pdfWrapper.classList.add('hidden');
        } else {
            if (pdfFileName) pdfFileName.textContent = file.name + ' — ' + formatSize(file.size);
            if (imageWrapper) imageWrapper.classList.add('hidden');
            if (pdfWrapper)   pdfWrapper.classList.remove('hidden');
        }
    }

    // ── 4. FILE INPUT EVENTS ─────────────────────────────────────────────────    // FILE PICKER — change event handled inline via onchange="spHandleWorkFile(this)"
    // See the inline <script> in form.html for spHandleWorkFile, spRemoveWorkFile, spHandlePhotoFile

    // DRAG AND DROP
    if (dropZone) {
        dropZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.style.borderColor = '#0B7A3B';
            dropZone.style.background  = '#F0FDF4';
        });

        dropZone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.style.borderColor = '';
            dropZone.style.background  = '';
        });

        dropZone.addEventListener('drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.style.borderColor = '';
            dropZone.style.background  = '';

            var files = e.dataTransfer ? e.dataTransfer.files : null;
            if (files && files.length > 0) {
                try {
                    var dt = new DataTransfer();
                    dt.items.add(files[0]);
                    if (workFile) {
                        workFile.files = dt.files;
                        // Trigger the global preview handler
                        if (typeof spHandleWorkFile === 'function') spHandleWorkFile(workFile);
                    }
                } catch (err) {
                    // DataTransfer not supported — just show preview
                    if (typeof spHandleWorkFile === 'function') {
                        // Fake the input for preview only
                        var fakeInput = { files: files };
                        spHandleWorkFile(fakeInput);
                    }
                }
            }
        });
    }

    // REMOVE FILE — handled via onclick="spRemoveWorkFile()" on the button in form.html

    // ── 7. OPTIONAL STUDENT PHOTO ────────────────────────────────────────────
    if (studentPhotoInput && studentPhotoName) {
        studentPhotoInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                studentPhotoName.textContent = this.files[0].name;
                studentPhotoName.style.color = '#0B7A3B';
            } else {
                studentPhotoName.textContent = 'Click to upload student portrait (optional)';
                studentPhotoName.style.color = '';
            }
        });
    }

    // ── 8. REAL-TIME MOBILE VALIDATION ───────────────────────────────────────
    if (mobileInput) {
        mobileInput.addEventListener('input', function () {
            var mobile = this.value;

            // Reset all indicators
            if (mobileStatusIcon) mobileStatusIcon.classList.add('hidden');
            if (mobileOk)         mobileOk.classList.add('hidden');
            if (mobileError)      mobileError.classList.add('hidden');
            if (mobileLoading)    mobileLoading.classList.add('hidden');
            if (mobileErrorMsg)   mobileErrorMsg.classList.add('hidden');
            mobileInput.style.borderColor = '';
            if (submitBtn) submitBtn.disabled = true;

            // Only check when exactly 10 digits
            if (/^\d{10}$/.test(mobile)) {
                if (mobileStatusIcon) mobileStatusIcon.classList.remove('hidden');
                if (mobileLoading)    mobileLoading.classList.remove('hidden');

                clearTimeout(checkTimeout);
                checkTimeout = setTimeout(function () {
                    var fd = new FormData();
                    fd.append('mobile', mobile);

                    fetch('/student-portal/api/check-mobile/', {
                        method: 'POST',
                        body: fd,
                        headers: { 'X-CSRFToken': getCookie('csrftoken') }
                    })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (mobileLoading) mobileLoading.classList.add('hidden');

                        if (data.exists) {
                            if (mobileError)    mobileError.classList.remove('hidden');
                            if (mobileErrorMsg) mobileErrorMsg.classList.remove('hidden');
                            mobileInput.style.borderColor = '#EF4444';
                        } else {
                            if (mobileOk) mobileOk.classList.remove('hidden');
                            mobileInput.style.borderColor = '#22C55E';
                            if (submitBtn) submitBtn.disabled = false;
                        }
                    })
                    .catch(function () {
                        if (mobileLoading) mobileLoading.classList.add('hidden');
                        // On network error, allow form to proceed
                        if (submitBtn) submitBtn.disabled = false;
                    });
                }, 600);
            }
        });
    }

    // ── 9. FORM SUBMISSION ───────────────────────────────────────────────────
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Validate file
            if (!workFile || !workFile.files || workFile.files.length === 0) {
                alert('Please upload your work (JPG, PNG, or PDF).');
                return;
            }

            // Validate consent
            var consentCheck = document.getElementById('consent');
            if (consentCheck && !consentCheck.checked) {
                alert('Please confirm your consent by checking the box.');
                return;
            }

            var originalText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Submitting...';
                submitBtn.disabled = true;
            }

            var fd = new FormData(form);

            fetch('/student-portal/api/submit/', {
                method: 'POST',
                body: fd,
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            })
            .then(function (r) {
                return r.json().then(function (data) {
                    return { ok: r.ok, data: data };
                });
            })
            .then(function (res) {
                if (res.ok) {
                    // Show success modal
                    var modal = document.getElementById('student-portal-success');
                    if (modal) modal.classList.remove('hidden');

                    var certId  = document.getElementById('cert-part-id');
                    var dlPdf   = document.getElementById('cert-download-pdf');
                    var dlPng   = document.getElementById('cert-download-png');
                    var shareWa = document.getElementById('cert-share-wa');

                    if (certId)  certId.textContent = res.data.participation_id || '';
                    if (dlPdf)   dlPdf.href  = res.data.certificate_pdf  || '#';
                    if (dlPng)   dlPng.href  = res.data.certificate_png  || '#';
                    if (shareWa) {
                        var msg = encodeURIComponent('I just participated in the Green Naroda \u2022 Clean Naroda Mission! ' + window.location.origin + (res.data.certificate_pdf || ''));
                        shareWa.href = 'https://wa.me/?text=' + msg;
                    }

                    // Reset form
                    form.reset();
                    if (previewContainer) previewContainer.classList.add('hidden');
                    if (imageWrapper)     imageWrapper.classList.add('hidden');
                    if (pdfWrapper)       pdfWrapper.classList.add('hidden');
                    if (previewImage)     previewImage.src = '';
                    if (currentObjectURL) { URL.revokeObjectURL(currentObjectURL); currentObjectURL = null; }
                    if (studentPhotoName) { studentPhotoName.textContent = 'Click to upload student portrait (optional)'; studentPhotoName.style.color = ''; }
                    if (mobileInput)      { mobileInput.style.borderColor = ''; }
                    if (mobileStatusIcon) mobileStatusIcon.classList.add('hidden');

                } else {
                    alert(res.data.error || res.data.message || 'Submission failed. Please try again.');
                    if (submitBtn) { submitBtn.innerHTML = originalText; submitBtn.disabled = false; }
                }
            })
            .catch(function (err) {
                console.error('Submit error:', err);
                alert('Network error. Please check your connection and try again.');
                if (submitBtn) { submitBtn.innerHTML = originalText; submitBtn.disabled = false; }
            });
        });
    }

}); // end DOMContentLoaded
