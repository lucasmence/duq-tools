// ========== State ==========
const state = {
  images: [], // Array of { id, file, dataUrl, name, width, height, size, timestamp }
  counter: 0,
};

// ========== DOM References ==========
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const btnSelect = document.getElementById('btnSelect');
const imageList = document.getElementById('imageList');
const emptyState = document.getElementById('emptyState');
const imageCountBadge = document.getElementById('imageCount');
const btnClearAll = document.getElementById('btnClearAll');
const btnSave = document.getElementById('btnSave');
const template = document.getElementById('imageCardTemplate');
const previewCanvas = document.getElementById('previewCanvas');
const previewContainer = document.getElementById('previewContainer');
const previewEmpty = document.getElementById('previewEmpty');
const previewDimensions = document.getElementById('previewDimensions');

// ========== Format Helpers ==========
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function generateId() {
  return 'img-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);
}

// ========== Toast System ==========
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer') || (() => {
    const el = document.createElement('div');
    el.id = 'toastContainer';
    el.className = 'toast-container';
    document.body.appendChild(el);
    return el;
  })();

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconSvg = type === 'error'
    ? '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M6 6L12 12M12 6L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
    : '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 9.5L7.5 11.5L12.5 6.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  toast.innerHTML = `
    <span class="toast-icon">${iconSvg}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M3 3L11 11M11 3L3 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  `;

  container.appendChild(toast);

  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.addEventListener('click', () => removeToast(toast));

  setTimeout(() => removeToast(toast), 4000);
}

function removeToast(toast) {
  if (toast.classList.contains('toast-exit')) return;
  toast.classList.add('toast-exit');
  setTimeout(() => toast.remove(), 300);
}

// ========== Image Processing ==========
function loadImage(file) {
  return new Promise((resolve, reject) => {
    if (!file.type || !file.type.startsWith('image/png')) {
      reject(new Error(`"${file.name}" is not a PNG file.`));
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;

      const img = new Image();
      img.onload = () => {
        resolve({
          id: generateId(),
          file,
          dataUrl,
          element: img,
          name: file.name,
          width: img.naturalWidth,
          height: img.naturalHeight,
          size: file.size,
          timestamp: Date.now(),
        });
      };
      img.onerror = () => reject(new Error(`Failed to load "${file.name}".`));
      img.src = dataUrl;
    };
    reader.onerror = () => reject(new Error(`Error reading "${file.name}".`));
    reader.readAsDataURL(file);
  });
}

// ========== Add Images to State ==========
async function addImages(files) {
  const validFiles = Array.from(files).filter(f =>
    f.type && f.type.startsWith('image/png')
  );

  if (validFiles.length === 0) {
    showToast('No valid PNG files found.', 'error');
    return;
  }

  if (validFiles.length !== files.length) {
    showToast(`${files.length - validFiles.length} file(s) ignored (only PNG accepted).`, 'error');
  }

  let addedCount = 0;
  for (const file of validFiles) {
    try {
      const imageData = await loadImage(file);
      state.images.push(imageData);
      addedCount++;
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  if (addedCount > 0) {
    showToast(`${addedCount} image(s) added successfully!`, 'success');
    renderList();
    updateUI();
  }
}

// ========== Remove Image ==========
function removeImage(id) {
  const card = document.querySelector(`.image-card[data-id="${id}"]`);
  if (card) {
    card.classList.add('removing');
    setTimeout(() => {
      state.images = state.images.filter(img => img.id !== id);
      renderList();
      updateUI();
    }, 280);
  } else {
    state.images = state.images.filter(img => img.id !== id);
    renderList();
    updateUI();
  }
}

// ========== Clear All ==========
function clearAll() {
  if (state.images.length === 0) return;
  state.images = [];
  renderList();
  updateUI();
  showToast('All images removed.', 'success');
}

// ========== Live Preview ==========
let previewRAF = null;

function renderPreview() {
  if (previewRAF) {
    cancelAnimationFrame(previewRAF);
    previewRAF = null;
  }

  previewRAF = requestAnimationFrame(() => {
    previewRAF = null;
    doRenderPreview();
  });
}

function doRenderPreview() {
  const count = state.images.length;

  if (count === 0) {
    previewCanvas.style.display = 'none';
    previewEmpty.style.display = 'flex';
    previewDimensions.classList.remove('visible');
    previewDimensions.textContent = '';
    return;
  }

  previewEmpty.style.display = 'none';
  previewCanvas.style.display = 'block';

  // Calculate full sprite sheet dimensions
  const maxWidth = Math.max(...state.images.map(img => img.width));
  const totalHeight = state.images.reduce((sum, img) => sum + img.height, 0);

  // Update dimension badge
  previewDimensions.textContent = `${maxWidth} × ${totalHeight} px`;
  previewDimensions.classList.add('visible');

  // Create off-screen canvas at full resolution
  const offscreen = document.createElement('canvas');
  offscreen.width = maxWidth;
  offscreen.height = totalHeight;
  const offCtx = offscreen.getContext('2d');

  // Draw each image vertically stacked, left-aligned
  let yOffset = 0;
  for (const img of state.images) {
    offCtx.drawImage(img.element, 0, yOffset);
    yOffset += img.height;
  }

  // Scale to fit preview container width
  const containerWidth = previewContainer.clientWidth - 2; // minus border
  const scale = Math.min(1, containerWidth / maxWidth);
  const displayWidth = Math.round(maxWidth * scale);
  const displayHeight = Math.round(totalHeight * scale);

  // Set canvas CSS size to fill container width
  previewCanvas.width = displayWidth;
  previewCanvas.height = displayHeight;
  previewCanvas.style.width = displayWidth + 'px';
  previewCanvas.style.height = displayHeight + 'px';

  const ctx = previewCanvas.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(offscreen, 0, 0, displayWidth, displayHeight);
}

// Resize observer for preview
const previewResizeObserver = new ResizeObserver(() => {
  if (state.images.length > 0) renderPreview();
});
previewResizeObserver.observe(previewContainer);

// ========== Export PNG (Sprite Sheet Vertical) ==========
function exportSpriteSheet() {
  if (state.images.length === 0) {
    showToast('Add at least one image before saving.', 'error');
    return;
  }

  btnSave.disabled = true;
  btnSave.classList.add('saving');
  btnSave.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5" stroke-dasharray="8 4"/>
    </svg>
    Saving...
  `;

  // Defer to next tick for UI update
  setTimeout(() => {
    try {
      // Calculate canvas dimensions
      const maxWidth = Math.max(...state.images.map(img => img.width));
      const totalHeight = state.images.reduce((sum, img) => sum + img.height, 0);

      // Create canvas with transparent background
      const canvas = document.createElement('canvas');
      canvas.width = maxWidth;
      canvas.height = totalHeight;

      const ctx = canvas.getContext('2d');

      // Draw each image vertically stacked, left-aligned
      let yOffset = 0;
      state.images.forEach(img => {
        ctx.drawImage(img.element, 0, yOffset);
        yOffset += img.height;
      });

      // Export as PNG with transparency preserved
      const link = document.createElement('a');
      link.download = 'duq-sprite-fusion.png';
      link.href = canvas.toDataURL('image/png');
      link.click();

      showToast('Sprite sheet saved successfully!', 'success');
    } catch (err) {
      showToast('Error generating PNG: ' + err.message, 'error');
    } finally {
      btnSave.disabled = false;
      btnSave.classList.remove('saving');
      btnSave.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M13.333 10.667v2A1.333 1.333 0 0112 14H4a1.333 1.333 0 01-1.333-1.333v-2M8 2v8M5.333 7.333L8 10.667l2.667-3.334" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Save Fusion
      `;
    }
  }, 50);
}

// ========== Render Image List ==========
function renderList() {
  // Remove old cards (keep empty state)
  const cards = imageList.querySelectorAll('.image-card');
  cards.forEach(c => c.remove());

  if (state.images.length === 0) {
    emptyState.style.display = 'flex';
    return;
  }

  emptyState.style.display = 'none';

  // Render images in the order of state.images array
  state.images.forEach((img, index) => {
    const card = template.content.cloneNode(true).querySelector('.image-card');
    card.setAttribute('data-id', img.id);

    const preview = card.querySelector('.image-card-preview img');
    preview.src = img.dataUrl;
    preview.alt = img.name;

    card.querySelector('.image-card-name').textContent = img.name;

    card.querySelector('.image-card-dimensions').textContent = `${img.width} × ${img.height} px`;
    card.querySelector('.image-card-size').textContent = formatFileSize(img.size);
    card.querySelector('.image-card-order').textContent = `#${index + 1}`;
    card.querySelector('.image-card-index').textContent = index + 1;

    // Remove button
    const removeBtn = card.querySelector('.image-card-remove');
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeImage(img.id);
    });

    // Drag handle — enable dragging on mousedown
    const handle = card.querySelector('.image-card-handle');
    card.setAttribute('draggable', 'false');

    handle.addEventListener('mousedown', (e) => {
      e.stopPropagation();
      card.setAttribute('draggable', 'true');
    });

    // Reset draggable if mouse leaves card without dragging
    card.addEventListener('mouseleave', () => {
      if (card.getAttribute('draggable') === 'true' && !card.classList.contains('dragging')) {
        card.setAttribute('draggable', 'false');
      }
    });

    // Touch support for mobile reordering
    handle.addEventListener('touchstart', (e) => onTouchStart(e, card), { passive: true });

    imageList.appendChild(card);
  });

  // Re-attach drag events to all cards
  attachDragEvents();

  // Update live preview
  renderPreview();
}

// ========== Drag-to-Reorder ==========
let dragSrcId = null;
let touchDragData = null; // { cardId, startY, clone }

function attachDragEvents() {
  const cards = imageList.querySelectorAll('.image-card');

  cards.forEach(card => {
    card.removeEventListener('dragstart', onDragStart);
    card.removeEventListener('dragend', onDragEnd);
    card.removeEventListener('dragover', onDragOver);
    card.removeEventListener('dragenter', onDragEnter);
    card.removeEventListener('dragleave', onDragLeave);
    card.removeEventListener('drop', onDrop);

    card.addEventListener('dragstart', onDragStart);
    card.addEventListener('dragend', onDragEnd);
    card.addEventListener('dragover', onDragOver);
    card.addEventListener('dragenter', onDragEnter);
    card.addEventListener('dragleave', onDragLeave);
    card.addEventListener('drop', onDrop);
  });
}

function onDragStart(e) {
  dragSrcId = this.dataset.id;
  this.classList.add('dragging');
  imageList.classList.add('drag-reordering');
  e.dataTransfer.effectAllowed = 'move';
  // Safari compatibility: set a dummy URL
  e.dataTransfer.setData('text/plain', this.dataset.id);
  e.dataTransfer.setData('text/uri-list', 'about:blank');
}

function onDragEnd() {
  this.classList.remove('dragging');
  imageList.classList.remove('drag-reordering');
  clearDropIndicators();
  resetDraggableAll();
  dragSrcId = null;
}

function onDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';

  // Real-time visual indicator
  if (this.dataset.id !== dragSrcId) {
    const rect = this.getBoundingClientRect();
    const y = e.clientY - rect.top;

    // Only update indicators when crossing the threshold
    const showBefore = y < rect.height / 2;
    const currentlyBefore = this.classList.contains('drop-before');
    const currentlyAfter = this.classList.contains('drop-after');

    if (showBefore && !currentlyBefore) {
      clearDropIndicators();
      this.classList.add('drop-before');
    } else if (!showBefore && !currentlyAfter) {
      clearDropIndicators();
      this.classList.add('drop-after');
    }
  }
}

function onDragEnter(e) {
  e.preventDefault();
  if (this.dataset.id !== dragSrcId) {
    imageList.classList.add('drag-reordering');
  }
}

function onDragLeave(e) {
  if (!this.contains(e.relatedTarget)) {
    this.classList.remove('drop-before', 'drop-after');
    // Check if we left the entire list
    if (!imageList.contains(e.relatedTarget)) {
      imageList.classList.remove('drag-reordering');
    }
  }
}

function onDrop(e) {
  e.preventDefault();
  e.stopPropagation();

  const sourceId = dragSrcId;
  const targetId = this.dataset.id;

  if (!sourceId || sourceId === targetId) {
    cleanupReorder();
    return;
  }

  performReorder(sourceId, targetId, e.clientY);
}

function performReorder(sourceId, targetId, clientY) {
  const sourceIdx = state.images.findIndex(img => img.id === sourceId);
  const targetIdx = state.images.findIndex(img => img.id === targetId);

  if (sourceIdx === -1 || targetIdx === -1) {
    cleanupReorder();
    return;
  }

  // Find the target card element to determine insert position
  const targetCard = document.querySelector(`.image-card[data-id="${targetId}"]`);
  if (!targetCard) {
    cleanupReorder();
    return;
  }

  const rect = targetCard.getBoundingClientRect();
  const y = clientY !== undefined ? clientY - rect.top : rect.height / 2;
  const insertBefore = y < rect.height / 2;

  // Reorder the array
  const [movedItem] = state.images.splice(sourceIdx, 1);
  const newTargetIdx = state.images.findIndex(img => img.id === targetId);
  const insertAt = insertBefore ? newTargetIdx : newTargetIdx + 1;
  state.images.splice(insertAt, 0, movedItem);

  cleanupReorder();
  renderList();
  updateUI();
}

function clearDropIndicators() {
  document.querySelectorAll('.drop-before, .drop-after').forEach(el => {
    el.classList.remove('drop-before', 'drop-after');
  });
}

function resetDraggableAll() {
  document.querySelectorAll('.image-card').forEach(c => {
    c.setAttribute('draggable', 'false');
  });
}

function cleanupReorder() {
  imageList.classList.remove('drag-reordering');
  clearDropIndicators();
  document.querySelectorAll('.image-card.dragging').forEach(el => {
    el.classList.remove('dragging');
  });
  resetDraggableAll();
  dragSrcId = null;
}

// ========== Touch Drag-to-Reorder (Mobile) ==========
function onTouchStart(e, card) {
  if (state.images.length < 2) return;

  const touch = e.touches[0];
  touchDragData = {
    cardId: card.dataset.id,
    startY: touch.clientY,
  };

  card.classList.add('dragging');
  imageList.classList.add('drag-reordering');

  // Create a visual clone that follows the finger
  const clone = card.cloneNode(true);
  clone.classList.add('dragging-clone');
  clone.style.position = 'fixed';
  clone.style.width = card.offsetWidth + 'px';
  clone.style.pointerEvents = 'none';
  clone.style.zIndex = '1000';
  clone.style.opacity = '0.85';
  clone.style.transform = 'scale(0.95)';
  clone.style.border = '2px solid var(--accent)';
  clone.style.borderRadius = 'var(--radius-md)';
  clone.style.boxShadow = '0 8px 32px rgba(0,0,0,0.5)';
  clone.style.left = card.getBoundingClientRect().left + 'px';
  clone.style.top = touch.clientY - 40 + 'px';
  document.body.appendChild(clone);
  touchDragData.clone = clone;

  document.addEventListener('touchmove', onTouchMove, { passive: false });
  document.addEventListener('touchend', onTouchEnd, { passive: false });
  document.addEventListener('touchcancel', onTouchCancel, { passive: false });
}

function onTouchMove(e) {
  e.preventDefault();
  if (!touchDragData) return;

  const touch = e.touches[0];

  // Move the visual clone
  if (touchDragData.clone) {
    touchDragData.clone.style.top = (touch.clientY - 40) + 'px';
  }

  // Find which card is under the finger
  const elementUnder = document.elementFromPoint(touch.clientX, touch.clientY);
  const cardUnder = elementUnder?.closest('.image-card');

  clearDropIndicators();

  if (cardUnder && cardUnder.dataset.id !== touchDragData.cardId) {
    const rect = cardUnder.getBoundingClientRect();
    const y = touch.clientY - rect.top;
    if (y < rect.height / 2) {
      cardUnder.classList.add('drop-before');
    } else {
      cardUnder.classList.add('drop-after');
    }
  }
}

function onTouchEnd(e) {
  document.removeEventListener('touchmove', onTouchMove);
  document.removeEventListener('touchend', onTouchEnd);
  document.removeEventListener('touchcancel', onTouchCancel);

  if (!touchDragData) return;

  // Find drop target from touch position
  const touch = e.changedTouches[0];
  const elementUnder = document.elementFromPoint(touch.clientX, touch.clientY);
  const cardUnder = elementUnder?.closest('.image-card');

  // Clean up clone
  if (touchDragData.clone) {
    touchDragData.clone.remove();
  }

  const sourceId = touchDragData.cardId;
  touchDragData = null;

  // Remove dragging from all cards
  document.querySelectorAll('.image-card.dragging').forEach(el => {
    el.classList.remove('dragging');
  });
  imageList.classList.remove('drag-reordering');
  clearDropIndicators();

  if (cardUnder && cardUnder.dataset.id !== sourceId) {
    performReorder(sourceId, cardUnder.dataset.id, touch.clientY);
  }
}

function onTouchCancel() {
  document.removeEventListener('touchmove', onTouchMove);
  document.removeEventListener('touchend', onTouchEnd);
  document.removeEventListener('touchcancel', onTouchCancel);

  if (touchDragData) {
    if (touchDragData.clone) touchDragData.clone.remove();
    touchDragData = null;
  }

  document.querySelectorAll('.image-card.dragging').forEach(el => {
    el.classList.remove('dragging');
  });
  imageList.classList.remove('drag-reordering');
  clearDropIndicators();
}

// ========== Update UI ==========
function updateUI() {
  const count = state.images.length;
  imageCountBadge.textContent = count;

  // Pop animation on counter
  imageCountBadge.classList.add('pop');
  setTimeout(() => imageCountBadge.classList.remove('pop'), 300);

  // Toggle clear button
  if (count > 0) {
    btnClearAll.classList.add('visible');
    btnSave.classList.add('visible');
  } else {
    btnClearAll.classList.remove('visible');
    btnSave.classList.remove('visible');
  }

  // Toggle drop zone style
  if (count > 0) {
    dropZone.classList.add('has-files');
  } else {
    dropZone.classList.remove('has-files');
  }
}

// ========== Drag & Drop Events ==========
// Prevent defaults for all drag events on the document
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  document.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

// Drag over: show overlay
dropZone.addEventListener('dragenter', (e) => {
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragover', (e) => {
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
  // Only remove overlay if we actually left the drop zone
  if (!dropZone.contains(e.relatedTarget)) {
    dropZone.classList.remove('drag-over');
  }
});

dropZone.addEventListener('drop', (e) => {
  dropZone.classList.remove('drag-over');
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    addImages(files);
  }
});

// ========== Click to Select ==========
btnSelect.addEventListener('click', (e) => {
  e.stopPropagation();
  fileInput.click();
});

dropZone.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    addImages(e.target.files);
  }
  fileInput.value = ''; // Reset so the same files can be selected again
});

// ========== Clear All ==========
btnClearAll.addEventListener('click', clearAll);

// ========== Export ==========
btnSave.addEventListener('click', exportSpriteSheet);

// ========== Keyboard Support ==========
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && state.images.length > 0) {
    // Focus the drop zone
    dropZone.focus();
  }
});

// Make drop zone focusable and keyboard-activatable
dropZone.setAttribute('tabindex', '0');
dropZone.setAttribute('role', 'button');
dropZone.setAttribute('aria-label', 'Area to drag PNG images. Click to select files.');

dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});

// ========== Splash Screen ==========
function hideSplash() {
  const splash = document.getElementById('splash');
  if (!splash || splash.classList.contains('hiding')) return;
  splash.classList.add('hiding');
  setTimeout(() => splash.remove(), 500);
}

// Auto-hide splash after 2 seconds
setTimeout(hideSplash, 2000);

// Also hide splash early if user clicks it
const splashEl = document.getElementById('splash');
if (splashEl) {
  splashEl.addEventListener('click', hideSplash);
}

// ========== Initial Render ==========
renderList();
updateUI();
