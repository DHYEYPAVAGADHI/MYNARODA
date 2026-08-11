import re

with open('templates/admin_panel/leadership_photos.html', 'r') as f:
    content = f.read()

# 1. Add Cropper CDN links
if 'cropperjs' not in content:
    content = content.replace(
        '{% block content %}',
        '{% block content %}\n<!-- Cropper.js -->\n<link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">\n<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>'
    )

# 2. Add Modal CSS
modal_css = """
  /* Crop Modal Styles */
  .crop-modal {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: 99999;
    align-items: center;
    justify-content: center;
  }
  .crop-modal-content {
    background: #fff;
    border-radius: 24px;
    padding: 24px;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  }
  .crop-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .crop-modal-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
  }
  .crop-container {
    width: 100%;
    height: 400px;
    background: #f3f4f6;
    border-radius: 12px;
    overflow: hidden;
  }
  .crop-modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
  }
  .btn-cancel {
    background: #f3f4f6;
    color: #374151;
    border: none;
    padding: 10px 20px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-save-crop {
    background: #15803D;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  /* Make cropper mask circular */
  .cropper-view-box,
  .cropper-face {
    border-radius: 50%;
  }
  
  .lp-btn-remove {
    background: #FEF2F2;
    color: #DC2626;
    border: 1px solid #FCA5A5;
    padding: 10px 16px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: var(--t);
    margin-top: 4px;
  }
  .lp-btn-remove:hover {
    background: #FEE2E2;
  }
"""
content = content.replace('</style>', modal_css + '\n</style>')

# 3. Update the committee_leaders loop to add Remove button and hidden field
old_committee_loop = """  {% for leader in committee_leaders %}
  <div class="lp-card">
    <form method="post" enctype="multipart/form-data">
      {% csrf_token %}
      
      <div class="lp-avatar-wrapper">
        {% if leader.url %}
          <img src="{{ leader.url }}" alt="{{ leader.name }}">
        {% else %}
          <div class="lp-avatar-placeholder">👤</div>
        {% endif %}
      </div>
      
      <div class="lp-name">{{ leader.name }}</div>
      <div class="lp-role">{{ leader.role }}</div>
      
      <div class="lp-actions">
        <label class="lp-btn-choose">
          Choose Photo
          <input type="file" name="{{ leader.field }}" accept="image/*" style="display:none;" onchange="previewImage(this, '{{ leader.field }}')">
        </label>
        
        <button type="submit" class="lp-btn-save" id="btn-save-{{ leader.field }}">
          Save Photo
        </button>
      </div>
    </form>
  </div>
  {% endfor %}"""

new_committee_loop = """  {% for leader in committee_leaders %}
  <div class="lp-card">
    <form method="post" enctype="multipart/form-data" id="form-{{ leader.field }}">
      {% csrf_token %}
      <input type="hidden" name="cropped_{{ leader.field }}" id="cropped-{{ leader.field }}">
      
      <div class="lp-avatar-wrapper">
        {% if leader.url %}
          <img src="{{ leader.url }}" alt="{{ leader.name }}" id="preview-img-{{ leader.field }}">
        {% else %}
          <div class="lp-avatar-placeholder" id="placeholder-{{ leader.field }}">👤</div>
          <img src="" alt="Preview" id="preview-img-{{ leader.field }}" style="display:none;">
        {% endif %}
      </div>
      
      <div class="lp-name">{{ leader.name }}</div>
      <div class="lp-role">{{ leader.role }}</div>
      
      <div class="lp-actions" id="actions-{{ leader.field }}">
        <label class="lp-btn-choose">
          Upload Photo
          <input type="file" accept="image/*" style="display:none;" onchange="openCropModal(this, '{{ leader.field }}')">
        </label>
        
        <button type="submit" class="lp-btn-save" id="btn-save-{{ leader.field }}" style="display:none;">
          Save Photo
        </button>
        
        {% if leader.url %}
        <button type="button" class="lp-btn-remove" onclick="removePhoto('{{ leader.field }}')">
          Remove
        </button>
        {% endif %}
      </div>
    </form>
    
    <form method="post" id="form-remove-{{ leader.field }}" style="display:none;">
        {% csrf_token %}
        <input type="hidden" name="remove_field" value="{{ leader.field }}">
    </form>
  </div>
  {% endfor %}"""

content = content.replace(old_committee_loop, new_committee_loop)

# 4. Add Modal HTML at the end before script
modal_html = """
<!-- Crop Modal -->
<div class="crop-modal" id="cropModal">
  <div class="crop-modal-content">
    <div class="crop-modal-header">
      <div class="crop-modal-title">Crop Portrait</div>
    </div>
    <div class="crop-container">
      <img id="cropImage" src="" style="max-width: 100%;">
    </div>
    <div class="crop-modal-footer">
      <button type="button" class="btn-cancel" onclick="closeCropModal()">Cancel</button>
      <button type="button" class="btn-save-crop" onclick="performCrop()">Crop & Save</button>
    </div>
  </div>
</div>
"""
content = content.replace('<script>', modal_html + '\n<script>')

# 5. Add JS logic for cropping
custom_js = """
let currentCropper = null;
let currentField = null;

function openCropModal(input, fieldName) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById('cropImage').src = e.target.result;
      document.getElementById('cropModal').style.display = 'flex';
      currentField = fieldName;
      
      if (currentCropper) {
        currentCropper.destroy();
      }
      
      currentCropper = new Cropper(document.getElementById('cropImage'), {
        aspectRatio: 1,
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.9,
        restore: false,
        guides: false,
        center: false,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
      });
    };
    reader.readAsDataURL(input.files[0]);
    // reset input so same file can be selected again
    input.value = '';
  }
}

function closeCropModal() {
  document.getElementById('cropModal').style.display = 'none';
  if (currentCropper) {
    currentCropper.destroy();
    currentCropper = null;
  }
}

function performCrop() {
  if (!currentCropper) return;
  
  // Get 512x512 cropped canvas
  const canvas = currentCropper.getCroppedCanvas({
    width: 512,
    height: 512,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  });
  
  const base64Image = canvas.toDataURL('image/jpeg', 0.9);
  
  // Update hidden field
  document.getElementById('cropped-' + currentField).value = base64Image;
  
  // Update Preview UI
  let img = document.getElementById('preview-img-' + currentField);
  let placeholder = document.getElementById('placeholder-' + currentField);
  
  if (placeholder) {
      placeholder.style.display = 'none';
  }
  img.src = base64Image;
  img.style.display = 'block';
  
  // Show save button, hide remove button
  document.getElementById('btn-save-' + currentField).style.display = 'block';
  let removeBtn = document.getElementById('actions-' + currentField).querySelector('.lp-btn-remove');
  if (removeBtn) {
      removeBtn.style.display = 'none';
  }
  let chooseBtn = document.getElementById('actions-' + currentField).querySelector('.lp-btn-choose');
  if (chooseBtn) chooseBtn.style.display = 'none';
  
  closeCropModal();
}

function removePhoto(fieldName) {
  if (confirm("Are you sure you want to remove this photo? The placeholder will be restored.")) {
      document.getElementById('form-remove-' + fieldName).submit();
  }
}
"""

content = content.replace('<script>\nfunction previewImage', '<script>\n' + custom_js + '\nfunction previewImage')

with open('templates/admin_panel/leadership_photos.html', 'w') as f:
    f.write(content)
print("Cropper added to leadership_photos.html")
