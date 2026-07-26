/**
 * Duq Sprite Manager — JSON texture editor for 2D game sprites.
 */

// ─── State ───────────────────────────────────────────────────────────────────
let animations = [];
let animationIdCounter = 0;

const DEFAULT_ANIMATION = {
  id: null,
  name: '',
  spriteDirectionLeft: 0,
  spriteDirectionTop: 0,
  spriteDirectionWidth: 96,
  spriteDirectionHeight: 96,
  spriteLimit: 288,
  spriteRange: 96,
  animated: true,
  reverseMode: false,
  loop: true,
  sideFlip: true,
  speed: 0.25,
  sound: ''
};

const REQUIRED_ANIMATIONS = ['stand'];

// ─── DOM References ──────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const el = {
  texturename:     $('texturename'),
  propGeneration:  $('propGeneration'),
  textureOriginalChance: $('textureOriginalChance'),
  front:           $('front'),
  lightR:          $('lightR'),
  lightG:          $('lightG'),
  lightB:          $('lightB'),
  lightA:          $('lightA'),
  lightRange:      $('lightRange'),
  lightIntensity:  $('lightIntensity'),
  dimWidth:        $('dimWidth'),
  dimHeight:       $('dimHeight'),
  trailFreq:       $('trailFreq'),
  animationsList:  $('animationsList'),
  jsonPreview:     $('jsonPreview'),
  emptyState:      $('emptyState'),
  btnAddAnimation: $('btnAddAnimation'),
  btnOpen:         $('btnOpen'),
  btnSave:         $('btnSave'),
  btnCopy:         $('btnCopy'),
  fileInput:       $('fileInput'),
  validationBadge: $('validationBadge'),
  colorPreview:    $('colorPreview'),
};

// ─── Color Preview ───────────────────────────────────────────────────────────
function updateColorPreview() {
  const r = parseInt(el.lightR.value) || 0;
  const g = parseInt(el.lightG.value) || 0;
  const b = parseInt(el.lightB.value) || 0;
  const a = parseFloat(el.lightA.value) || 0;
  el.colorPreview.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
}

// ─── Animation Template ──────────────────────────────────────────────────────
function createAnimation(data = {}) {
  return {
    ...DEFAULT_ANIMATION,
    ...data,
    id: animationIdCounter++,
  };
}

// ─── Render Animations ───────────────────────────────────────────────────────
function renderAnimations() {
  const container = el.animationsList;
  container.innerHTML = '';

  if (animations.length === 0) {
    container.innerHTML = '<div class="empty-hint" style="text-align:center;padding:20px;color:var(--text-muted);font-size:13px;">No animations. Click "Add Animation" to get started.</div>';
    return;
  }

  animations.forEach((anim, index) => {
    const card = document.createElement('div');
    card.className = 'animation-card' + (isRequiredAnimation(anim.name) ? ' required-card' : '');
    card.dataset.index = index;

    const isRequired = isRequiredAnimation(anim.name);
    const isCollapsed = anim._collapsed || false;

    card.innerHTML = `
      <div class="animation-header" data-toggle>
        <div class="animation-header-left">
          <span class="anim-indicator"></span>
          <span class="animation-name-label">${escapeHtml(anim.name) || '(unnamed)'}</span>
          ${isRequired ? '<span class="anim-required-badge">required</span>' : ''}
        </div>
        <div style="display:flex;align-items:center;gap:4px;">
          <button class="btn-eye${isPreviewActive(anim) ? ' active' : ''}" title="Animation preview" data-eye="${anim.id}">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
          <span style="font-size:11px;color:var(--text-muted);">#${index + 1}</span>
          ${!isRequired ? `<button class="btn-danger btn-remove" title="Remove animation">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 4h10M5 4V2.5A1.5 1.5 0 016.5 1h1A1.5 1.5 0 019 2.5V4m1 0v7.5a1.5 1.5 0 01-1.5 1.5h-5A1.5 1.5 0 012 11.5V4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>` : ''}
        </div>
      </div>
      <div class="animation-body" style="display:${isCollapsed ? 'none' : 'grid'};">
        <div class="field-group full-width">
          <label>Animation Name</label>
          <input type="text" class="anim-name" value="${escapeHtml(anim.name)}" placeholder="e.g. walk" ${isRequired ? 'readonly' : ''}>
        </div>
        <div class="field-group">
          <label>Sprite Left</label>
          <input type="number" class="anim-left" value="${anim.spriteDirectionLeft}" min="0">
        </div>
        <div class="field-group">
          <label>Sprite Top</label>
          <input type="number" class="anim-top" value="${anim.spriteDirectionTop}" min="0">
        </div>
        <div class="field-group">
          <label>Sprite Width</label>
          <input type="number" class="anim-width" value="${anim.spriteDirectionWidth}" min="1">
        </div>
        <div class="field-group">
          <label>Sprite Height</label>
          <input type="number" class="anim-height" value="${anim.spriteDirectionHeight}" min="1">
        </div>
        <div class="field-group">
          <label>Sprite Limit</label>
          <div class="input-with-btn">
            <input type="number" class="anim-limit" value="${anim.spriteLimit}" min="0">
            <button class="btn-limit-plus" title="Add sprite range to sprite limit">+</button>
          </div>
        </div>
        <div class="field-group">
          <label>Sprite Range</label>
          <input type="number" class="anim-range" value="${anim.spriteRange}" min="1">
        </div>
        <div class="field-group full-width">
          <label>Speed</label>
          <input type="number" class="anim-speed" value="${anim.speed}" min="0" step="0.01">
        </div>
        <div class="checkbox-row">
          <div class="checkbox-field">
            <input type="checkbox" class="anim-animated" ${anim.animated ? 'checked' : ''}>
            <label>Animated</label>
          </div>
          <div class="checkbox-field">
            <input type="checkbox" class="anim-reverse" ${anim.reverseMode ? 'checked' : ''}>
            <label>Reverse Mode</label>
          </div>
          <div class="checkbox-field">
            <input type="checkbox" class="anim-loop" ${anim.loop ? 'checked' : ''}>
            <label>Loop</label>
          </div>
          <div class="checkbox-field">
            <input type="checkbox" class="anim-sideflip" ${anim.sideFlip ? 'checked' : ''}>
            <label>Side Flip</label>
          </div>
        </div>
        <div class="field-group full-width">
          <label>Sound (optional)</label>
          <input type="text" class="anim-sound" value="${escapeHtml(anim.sound || '')}" placeholder="e.g. units/skeleton-death">
        </div>
      </div>
    `;

    // Toggle collapse + select animation + show preview
    const header = card.querySelector('[data-toggle]');
    const body = card.querySelector('.animation-body');
    header.addEventListener('click', (e) => {
      if (e.target.closest('.btn-remove')) return;
      // Select this animation for spritesheet preview
      selectAnimation(index);
      // Show animation preview if spritesheet is loaded and animated
      if (spritesheetImage && anim.animated) {
        showAnimationPreview(anim);
      }
      // Toggle collapse
      const isHidden = body.style.display === 'none';
      body.style.display = isHidden ? 'grid' : 'none';
      anim._collapsed = !isHidden;
    });

    // Eye button — toggle animation preview
    const eyeBtn = card.querySelector('.btn-eye');
    if (eyeBtn) {
      eyeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectAnimation(index);
        toggleAnimationPreview(anim);
        // Update eye button active state on all cards
        renderAnimations();
      });
    }

    // Remove button
    const removeBtn = card.querySelector('.btn-remove');
    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        // If preview is showing for this animation, stop it
        if (isPreviewActive(anim)) {
          stopAnimationPreview();
        }
        animations.splice(index, 1);
        if (selectedAnimIndex >= animations.length) {
          selectedAnimIndex = Math.max(0, animations.length - 1);
        }
        renderAnimations();
        updateJSONPreview();
        refreshSpritesheet();
      });
    }

    // Input change handlers — sync data + update preview + refresh spritesheet
    const inputs = card.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        syncAnimationFromDOM(index, card);
        // Sync animation preview if this animation is being previewed
        if (animPreviewState.active && animPreviewState.anim === animations[index]) {
          syncAnimPreview();
        }
        updateJSONPreview();
        refreshSpritesheet();
      });
      input.addEventListener('change', () => {
        syncAnimationFromDOM(index, card);
        // Sync animation preview if this animation is being previewed
        if (animPreviewState.active && animPreviewState.anim === animations[index]) {
          syncAnimPreview();
        }
        updateJSONPreview();
        refreshSpritesheet();
      });
    });

    // Select animation when any input inside card gets focus
    const allFields = card.querySelectorAll('.anim-name, .anim-left, .anim-top, .anim-width, .anim-height, .anim-limit, .anim-range, .anim-speed, .anim-sound');
    allFields.forEach(field => {
      field.addEventListener('focus', () => {
        selectAnimation(index);
      });
    });

    // + button — add sprite range to sprite limit
    const limitPlusBtn = card.querySelector('.btn-limit-plus');
    if (limitPlusBtn) {
      limitPlusBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const range = parseFloat(card.querySelector('.anim-range')?.value) || 0;
        const currentLimit = parseFloat(card.querySelector('.anim-limit')?.value) || 0;
        const newLimit = currentLimit + range;
        card.querySelector('.anim-limit').value = newLimit;
        syncAnimationFromDOM(index, card);
        if (animPreviewState.active && animPreviewState.anim === animations[index]) {
          syncAnimPreview();
        }
        updateJSONPreview();
        refreshSpritesheet();
      });
    }

    container.appendChild(card);

    // Card-level click — select animation and show preview when clicking
    // any part of the card (body area), not just the header
    card.addEventListener('click', (e) => {
      // Don't interfere with interactive elements (inputs, remove, eye, limit+)
      if (e.target.closest('input, .btn-remove, .btn-eye, .btn-limit-plus')) return;
      // Header already handled in its own listener — avoid double-firing
      if (e.target.closest('[data-toggle]')) return;

      selectAnimation(index);
      if (spritesheetImage && anim.animated) {
        showAnimationPreview(anim);
      }
    });
  });
}

// ─── Sync animation data from DOM back into state ────────────────────────────
function syncAnimationFromDOM(index, card) {
  if (!card) {
    card = el.animationsList.children[index];
    if (!card) return;
  }

  const anim = animations[index];
  if (!anim) return;

  const newName = card.querySelector('.anim-name')?.value || '';
  const wasRequired = isRequiredAnimation(anim.name);
  const isRequiredNow = isRequiredAnimation(newName);

  anim.name = newName;
  anim.spriteDirectionLeft  = parseFloat(card.querySelector('.anim-left')?.value) || 0;
  anim.spriteDirectionTop   = parseFloat(card.querySelector('.anim-top')?.value) || 0;
  anim.spriteDirectionWidth  = parseFloat(card.querySelector('.anim-width')?.value) || 1;
  anim.spriteDirectionHeight = parseFloat(card.querySelector('.anim-height')?.value) || 1;
  anim.spriteLimit  = parseFloat(card.querySelector('.anim-limit')?.value) || 0;
  anim.spriteRange  = parseFloat(card.querySelector('.anim-range')?.value) || 1;
  anim.speed        = parseFloat(card.querySelector('.anim-speed')?.value) || 0;
  anim.animated     = card.querySelector('.anim-animated')?.checked || false;
  anim.reverseMode  = card.querySelector('.anim-reverse')?.checked || false;
  anim.loop         = card.querySelector('.anim-loop')?.checked || false;
  anim.sideFlip     = card.querySelector('.anim-sideflip')?.checked || false;
  anim.sound        = card.querySelector('.anim-sound')?.value || '';

  // If required status changed, re-render all cards (shows/hides remove button)
  if (wasRequired !== isRequiredNow) {
    renderAnimations();
    return;
  }

  // Update card label
  const nameLabel = card.querySelector('.animation-name-label');
  if (nameLabel) nameLabel.textContent = anim.name || '(unnamed)';

  const badgeEl = card.querySelector('.anim-required-badge');
  if (isRequiredNow) {
    card.classList.add('required-card');
    if (!badgeEl) {
      const left = card.querySelector('.animation-header-left');
      const badge = document.createElement('span');
      badge.className = 'anim-required-badge';
      badge.textContent = 'required';
      left.appendChild(badge);
    }
  } else {
    card.classList.remove('required-card');
    if (badgeEl) badgeEl.remove();
  }
}

// ─── Sync all animations from DOM ────────────────────────────────────────────
function syncAllAnimations() {
  const cards = el.animationsList.querySelectorAll('.animation-card');
  cards.forEach((card, i) => {
    if (i < animations.length) {
      syncAnimationFromDOM(i, card);
    }
  });
}

// ─── Build JSON ──────────────────────────────────────────────────────────────
function buildJSON() {
  syncAllAnimations();

  const data = {};

  // texturename (required)
  const tn = el.texturename.value.trim();
  if (tn) {
    data.texturename = tn;
  }

  // prop-generation
  const pg = el.propGeneration.value.trim();
  if (pg) {
    data['prop-generation'] = pg;
  }

  // texture-original-chance
  const toc = parseInt(el.textureOriginalChance.value);
  if (!isNaN(toc)) {
    data['texture-original-chance'] = toc;
  }

  // front
  data['front'] = el.front.checked;

  // light color (only if any value is set)
  const lr = parseInt(el.lightR.value);
  const lg = parseInt(el.lightG.value);
  const lb = parseInt(el.lightB.value);
  const la = parseInt(el.lightA.value);
  if (!isNaN(lr) || !isNaN(lg) || !isNaN(lb) || !isNaN(la)) {
    data['light-color'] = {
      red:   isNaN(lr) ? 0 : lr,
      green: isNaN(lg) ? 0 : lg,
      blue:  isNaN(lb) ? 0 : lb,
      alpha: isNaN(la) ? 255 : la,
    };
  }

  // light range
  const lrVal = parseFloat(el.lightRange.value);
  if (!isNaN(lrVal) && el.lightRange.value !== '') {
    data['light-range'] = lrVal;
  }

  // light intensity
  const liVal = parseFloat(el.lightIntensity.value);
  if (!isNaN(liVal) && el.lightIntensity.value !== '') {
    data['light-intensity'] = liVal;
  }

  // dimensions
  const dw = parseInt(el.dimWidth.value);
  const dh = parseInt(el.dimHeight.value);
  if (!isNaN(dw)) data['dimension-width'] = dw;
  if (!isNaN(dh)) data['dimension-height'] = dh;

  // trail frequency
  const tf = parseFloat(el.trailFreq.value);
  if (!isNaN(tf) && el.trailFreq.value !== '') {
    data['motion-trail-frequency'] = tf;
  }

  // animations
  if (animations.length > 0) {
    data.animation = animations.map(anim => {
      const entry = {};
      entry['sprite-direction-left']   = anim.spriteDirectionLeft;
      entry['sprite-direction-top']    = anim.spriteDirectionTop;
      entry['sprite-direction-width']  = anim.spriteDirectionWidth;
      entry['sprite-direction-height'] = anim.spriteDirectionHeight;
      entry['sprite-limit']  = anim.spriteLimit;
      entry['sprite-range']  = anim.spriteRange;
      entry['animated']      = anim.animated;
      entry['reverse-mode']  = anim.reverseMode;
      entry['loop']          = anim.loop;
      entry['side-flip']     = anim.sideFlip;
      entry['speed']         = anim.speed;
      entry['name']          = anim.name || 'unnamed';
      if (anim.sound) {
        entry['sound'] = anim.sound;
      }
      return entry;
    });
  }

  return data;
}

// ─── Syntax-highlighted JSON (VS Code Dark+ inspired) ───────────────────────
function highlightJSON(obj) {
  const json = JSON.stringify(obj, null, 4);
  if (!json) return '';

  // HTML-escape first, then colorize in a single regex pass
  const escaped = json
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Single-pass tokenizer that matches all JSON token types left-to-right.
  // Order within the alternation determines priority:
  //   1 key  (quoted string followed by colon, with lookahead so colon is not consumed)
  //   2 string value (colon + quoted string)
  //   3 number value
  //   4 boolean value
  //   5 null value
  //   6 structural brackets
  //   7 comma
  //   8 colon (fallback — any colon not already consumed by key or value patterns)
  return escaped.replace(
    /("(?:[^"\\]|\\.)*")\s*(?=:)|:\s*("(?:[^"\\]|\\.)*")|:\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|:\s*(true|false)|:\s*(null)|([\[\]\{\}])|(,)|(:)/g,
    (_match, key, strVal, numVal, boolVal, nullVal, bracket, comma, colon) => {
      if (key)                return `<span class="json-key">${key}</span>`;
      if (strVal)             return `: <span class="json-string">${strVal}</span>`;
      if (numVal !== undefined) return `: <span class="json-number">${numVal}</span>`;
      if (boolVal)            return `: <span class="json-boolean">${boolVal}</span>`;
      if (nullVal)            return `: <span class="json-null">${nullVal}</span>`;
      if (bracket)            return `<span class="json-bracket">${bracket}</span>`;
      if (comma)              return `<span class="json-punctuation">${comma}</span>`;
      if (colon)              return `<span class="json-punctuation">:</span>`;
      return _match;
    }
  );
}

// ─── Update JSON Preview ─────────────────────────────────────────────────────
function updateJSONPreview() {
  const data = buildJSON();
  const hasTextureName = !!data.texturename;
  const hasStand = animations.some(a => a.name === 'stand');

  // Validate
  let valid = true;
  let errors = [];

  if (!hasTextureName) {
    valid = false;
    errors.push('"texturename" is required');
  }
  if (!hasStand) {
    valid = false;
    errors.push('Animation "stand" is required');
  }

  const badge = el.validationBadge;
  if (valid) {
    badge.textContent = '✓ Valid';
    badge.className = 'validation-badge valid';
  } else {
    badge.textContent = '✗ ' + errors.join(', ');
    badge.className = 'validation-badge invalid';
  }

  // Render JSON
  el.jsonPreview.innerHTML = highlightJSON(data);
  el.emptyState.style.display = 'none';
  el.jsonPreview.style.display = 'block';
}

// ─── Add Animation ───────────────────────────────────────────────────────────
function addAnimation(data = {}, doRender = true) {
  const anim = createAnimation(data);
  animations.push(anim);
  if (doRender) {
    renderAnimations();
    updateJSONPreview();
  }
}

// ─── Check if name is a required animation ───────────────────────────────────
function isRequiredAnimation(name) {
  return REQUIRED_ANIMATIONS.includes(name);
}

// ─── Clear current project ─────────────────────────────────────────────────
function clearCurrentProject() {
  currentProject = null;
  projectDirHandle = null;
  texturesDirHandle = null;
  updateProjectStatus(false, 'No project');
  localStorage.removeItem(STORAGE_KEY_CURRENT);
  renderRecentProjects();
}

// ─── Load from JSON object ──────────────────────────────────────────────────
function loadFromJSON(data) {
  // texturename
  el.texturename.value = data.texturename || '';

  // prop-generation
  el.propGeneration.value = data['prop-generation'] ?? '';

  // texture-original-chance
  el.textureOriginalChance.value = data['texture-original-chance'] ?? '';

  // front
  el.front.checked = data['front'] ?? false;

  // light color
  if (data['light-color']) {
    el.lightR.value = data['light-color'].red ?? '';
    el.lightG.value = data['light-color'].green ?? '';
    el.lightB.value = data['light-color'].blue ?? '';
    el.lightA.value = data['light-color'].alpha ?? '';
  } else {
    el.lightR.value = '';
    el.lightG.value = '';
    el.lightB.value = '';
    el.lightA.value = '';
  }

  // light range
  el.lightRange.value = data['light-range'] ?? '';

  // light intensity
  el.lightIntensity.value = data['light-intensity'] ?? '';

  // dimensions
  el.dimWidth.value = data['dimension-width'] ?? '';
  el.dimHeight.value = data['dimension-height'] ?? '';

  // trail frequency
  el.trailFreq.value = data['motion-trail-frequency'] ?? '';

  // animations (batch without re-rendering on each add)
  animations = [];
  animationIdCounter = 0;

  if (data.animation && Array.isArray(data.animation)) {
    data.animation.forEach(animData => {
      addAnimation({
        name: animData.name || '',
        spriteDirectionLeft:   animData['sprite-direction-left'] ?? 0,
        spriteDirectionTop:    animData['sprite-direction-top'] ?? 0,
        spriteDirectionWidth:  animData['sprite-direction-width'] ?? 96,
        spriteDirectionHeight: animData['sprite-direction-height'] ?? 96,
        spriteLimit:  animData['sprite-limit'] ?? 0,
        spriteRange:  animData['sprite-range'] ?? 96,
        animated:     animData['animated'] ?? true,
        reverseMode:  animData['reverse-mode'] ?? false,
        loop:         animData['loop'] ?? true,
        sideFlip:     animData['side-flip'] ?? true,
        speed:        animData['speed'] ?? 0.25,
        sound:        animData['sound'] || '',
      }, false); // doRender = false (batch)
    });
  }

  // Stop any playing animation preview
  stopAnimationPreview();

  updateColorPreview();
  renderAnimations();
  updateJSONPreview();
  refreshSpritesheet();

  // Auto-load spritesheet from project resources/sprites/<texturename>
  autoLoadSpritesheet();

  // Hide splash screen if it's visible (file was loaded successfully)
  if (splashEl && splashEl.style.display !== 'none') {
    hideSplashScreen();
  }
}

// ─── Open JSON File (with File System Access API support) ────────────────────
async function openFile() {
  // Try the modern File System Access API first
  if ('showOpenFilePicker' in window && projectDirHandle) {
    const texturesDir = await getTexturesDirHandle();
    if (texturesDir) {
      try {
        const [fileHandle] = await window.showOpenFilePicker({
          types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
          startIn: texturesDir,
          multiple: false,
        });
        const file = await fileHandle.getFile();
        const text = await file.text();
        try {
          const data = JSON.parse(text);
          lastOpenedJsonHandle = fileHandle;
          loadFromJSON(data);
        } catch (err) {
          lastOpenedJsonHandle = null;
          alert('Error reading JSON file: ' + err.message);
        }
        return;
      } catch (err) {
        lastOpenedJsonHandle = null;
        // User cancelled or API failed — fall through to fallback
        if (err.name === 'AbortError') return;
      }
    }
  }
  // Fallback: use regular file input
  el.fileInput.click();
}

function handleFileOpen(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      lastOpenedJsonHandle = null; // No filesystem handle from regular file input
      loadFromJSON(data);
    } catch (err) {
      alert('Error reading JSON file: ' + err.message);
    }
  };
  reader.readAsText(file);
  event.target.value = ''; // Reset so user can open same file again
}

// ─── Save JSON File (with File System Access API support) ────────────────────
async function saveFile() {
  syncAllAnimations();
  const data = buildJSON();

  // Validate before saving
  if (!data.texturename) {
    alert('The "texturename" field is required.');
    return;
  }
  if (!animations.some(a => a.name === 'stand')) {
    alert('You need at least one animation with name "stand".');
    return;
  }

  const json = JSON.stringify(data, null, 4);
  const filename = (data.texturename || 'sprite').replace(/[\/\\]/g, '_') + '.json';

  // Try the modern File System Access API first
  if ('showSaveFilePicker' in window) {
    let startDir = null;
    if (projectDirHandle) {
      startDir = await getTexturesDirHandle();
    }
    try {
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
        startIn: startDir || 'downloads',
      });
      const writable = await fileHandle.createWritable();
      await writable.write(json);
      await writable.close();
      return;
    } catch (err) {
      // User cancelled — do nothing
      if (err.name === 'AbortError') return;
      // Fall through to fallback on other errors
    }
  }

  // Fallback: download as blob
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── Copy JSON to clipboard ──────────────────────────────────────────────────
function copyJSON() {
  syncAllAnimations();
  const data = buildJSON();
  const json = JSON.stringify(data, null, 4);

  navigator.clipboard.writeText(json).then(() => {
    const originalText = el.btnCopy.innerHTML;
    el.btnCopy.innerHTML = '✓ Copied!';
    setTimeout(() => {
      el.btnCopy.innerHTML = originalText;
    }, 1500);
  }).catch(() => {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = json;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    alert('JSON copied to clipboard!');
  });
}

// ─── Escape HTML ─────────────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SPRITESHEET PREVIEW
// ═══════════════════════════════════════════════════════════════════════════════

let spritesheetImage = null;
let spritesheetFilename = '';
let selectedAnimIndex = 0;
let spriteZoom = 1;

// DOM refs for spritesheet
const spriteEl = {
  btnLoad:       $('btnLoadSpritesheet'),
  fileInput:     $('spritesheetInput'),
  modal:         $('spritesheetModal'),
  header:        $('spriteModalHeader'),
  title:         $('spriteModalTitle'),
  canvas:        $('spriteCanvas'),
  wrapper:       $('spriteCanvasWrapper'),
  emptyState:    $('spriteEmptyState'),
  btnEmptyLoad:  $('btnSpriteEmptyLoad'),
  btnLoadInline: $('btnLoadSpritesheetInline'),
  zoomBadge:     $('spriteZoomBadge'),
  btnZoomIn:     $('btnZoomIn'),
  btnZoomOut:    $('btnZoomOut'),
  btnClose:      $('btnCloseModal'),
  coords:        $('spriteCoords'),
};

// Handle to the last JSON file opened via File System Access API (used for spritesheet fallback)
let lastOpenedJsonHandle = null;

// ─── Load Spritesheet ──────────────────────────────────────────────────────
function openSpritesheet() {
  spriteEl.fileInput.click();
}

function handleSpritesheetLoad(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Stop any playing animation preview
  stopAnimationPreview();

  spritesheetFilename = file.name;

  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      spritesheetImage = img;
      spriteZoom = 1;
      showSpritesheetModal();
      renderSpritesheet();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

// ─── Show / Hide Panel Content ───────────────────────────────────
function showSpritesheetModal() {
  spriteEl.title.textContent = spritesheetFilename || 'Spritesheet';
  spriteEl.emptyState.style.display = 'none';
  spriteEl.wrapper.style.display = 'block';
}

function closeSpritesheetModal() {
  spritesheetImage = null;
  spritesheetFilename = '';
  stopAnimationPreview();
  spriteEl.wrapper.style.display = 'none';
  spriteEl.emptyState.style.display = 'flex';
  spriteEl.title.textContent = 'Spritesheet';
  spriteEl.coords.textContent = '—';
}

// ─── Render Canvas ─────────────────────────────────────────────────────────
function renderSpritesheet() {
  if (!spritesheetImage) return;

  const canvas = spriteEl.canvas;
  const ctx = canvas.getContext('2d');
  const img = spritesheetImage;

  const w = Math.round(img.width * spriteZoom);
  const h = Math.round(img.height * spriteZoom);

  canvas.width = w;
  canvas.height = h;

  // Checkerboard is handled by CSS on the wrapper; clear transparent
  ctx.clearRect(0, 0, w, h);

  // Draw the spritesheet
  ctx.drawImage(img, 0, 0, w, h);

  // Draw overlays for selected animation
  const anim = getSelectedAnimation();
  if (anim) {
    drawSpriteOverlays(ctx, anim, spriteZoom);
  }

  // Update zoom badge
  spriteEl.zoomBadge.textContent = Math.round(spriteZoom * 100) + '%';
}

// ─── Get Selected Animation ────────────────────────────────────────────────
function getSelectedAnimation() {
  if (animations.length === 0) return null;
  if (selectedAnimIndex < 0 || selectedAnimIndex >= animations.length) {
    selectedAnimIndex = 0;
  }
  return animations[selectedAnimIndex];
}

// ─── Draw Overlays ─────────────────────────────────────────────────────────
function drawSpriteOverlays(ctx, anim, zoom) {
  const left   = anim.spriteDirectionLeft * zoom;
  const top    = anim.spriteDirectionTop * zoom;
  const width  = anim.spriteDirectionWidth * zoom;
  const height = anim.spriteDirectionHeight * zoom;

  // ── Red rectangle: bounding box (direction area) ──
  ctx.strokeStyle = 'rgba(255, 60, 60, 0.9)';
  ctx.lineWidth = Math.max(1.5, 2 * zoom);
  ctx.strokeRect(left, top, width, height);

  // Semi-transparent red fill
  ctx.fillStyle = 'rgba(255, 60, 60, 0.08)';
  ctx.fillRect(left, top, width, height);

  // ── Green rectangle: dimension (centered within bounding box) ──
  const dimW = parseInt(el.dimWidth.value);
  const dimH = parseInt(el.dimHeight.value);
  if (!isNaN(dimW) && !isNaN(dimH) && dimW > 0 && dimH > 0) {
    const dimLeft   = (left + width  / 2) - (dimW * zoom) / 2;
    const dimTop    = (top  + height / 2) - (dimH * zoom) / 2;
    const dimWidth  = dimW * zoom;
    const dimHeight = dimH * zoom;

    ctx.strokeStyle = 'rgba(52, 211, 153, 0.9)';
    ctx.lineWidth = Math.max(1.5, 2 * zoom);
    ctx.strokeRect(dimLeft, dimTop, dimWidth, dimHeight);

    ctx.fillStyle = 'rgba(52, 211, 153, 0.12)';
    ctx.fillRect(dimLeft, dimTop, dimWidth, dimHeight);

    // Crosshair lines to show center alignment
    ctx.strokeStyle = 'rgba(52, 211, 153, 0.2)';
    ctx.lineWidth = Math.max(0.5, 1 * zoom);
    ctx.setLineDash([3 * zoom, 3 * zoom]);
    // Horizontal center line
    const centerY = top + height / 2;
    ctx.beginPath();
    ctx.moveTo(left, centerY);
    ctx.lineTo(left + width, centerY);
    ctx.stroke();
    // Vertical center line
    const centerX = left + width / 2;
    ctx.beginPath();
    ctx.moveTo(centerX, top);
    ctx.lineTo(centerX, top + height);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // ── Blue rectangles: frames (iterating X by sprite-range) ──
  const limit = anim.spriteLimit;
  const range = anim.spriteRange;

  if (limit > 0 && range > 0) {
    const frameWidth  = anim.spriteDirectionWidth * zoom;
    const frameHeight = anim.spriteDirectionHeight * zoom;
    const frameRange  = range * zoom;
    const baseX = anim.spriteDirectionLeft * zoom;
    const baseY = anim.spriteDirectionTop * zoom;

    ctx.strokeStyle = 'rgba(60, 140, 255, 0.8)';
    ctx.lineWidth = Math.max(1, 1.5 * zoom);
    ctx.fillStyle = 'rgba(60, 140, 255, 0.12)';

    let offsetX = 0;
    let frameIndex = 0;
    while (offsetX <= limit) {
      const fx = baseX + offsetX;
      const fy = baseY;

      ctx.fillRect(fx, fy, frameWidth, frameHeight);
      ctx.strokeRect(fx, fy, frameWidth, frameHeight);

      // Frame number label
      ctx.fillStyle = 'rgba(60, 140, 255, 0.9)';
      ctx.font = `bold ${Math.max(9, Math.round(11 * zoom))}px sans-serif`;
      ctx.textBaseline = 'top';
      ctx.fillText(String(frameIndex + 1), fx + 3, fy + 3);
      ctx.fillStyle = 'rgba(60, 140, 255, 0.12)';

      offsetX += frameRange;
      frameIndex++;
    }
  }
}

// (Drag and resize removed — spritesheet is now a fixed panel)

// ─── Zoom ──────────────────────────────────────────────────────────────────
function zoomIn() {
  spriteZoom = Math.min(10, spriteZoom * 1.25);
  renderSpritesheet();
}

function zoomOut() {
  spriteZoom = Math.max(0.1, spriteZoom / 1.25);
  renderSpritesheet();
}

// ─── Mouse tracking on canvas ──────────────────────────────────────────────
function onCanvasMouseMove(e) {
  if (!spritesheetImage) return;
  const rect = spriteEl.canvas.getBoundingClientRect();
  const x = Math.round((e.clientX - rect.left) / spriteZoom);
  const y = Math.round((e.clientY - rect.top) / spriteZoom);
  spriteEl.coords.textContent = `${x}, ${y}px`;
}

function onCanvasMouseLeave() {
  spriteEl.coords.textContent = '—';
}  // ─── Canvas click — set sprite-limit to clicked frame ────────────────
async function onCanvasClick(e) {
  if (!spritesheetImage) return;

  const anim = getSelectedAnimation();
  if (!anim) return;

  const rect = spriteEl.canvas.getBoundingClientRect();
  const spriteX = (e.clientX - rect.left) / spriteZoom;
  const spriteY = (e.clientY - rect.top) / spriteZoom;

  const range = anim.spriteRange;
  const limit = anim.spriteLimit;
  if (range <= 0 || limit <= 0) return;

  const baseX = anim.spriteDirectionLeft;
  const topY = anim.spriteDirectionTop;
  const height = anim.spriteDirectionHeight;
  const width = anim.spriteDirectionWidth;

  // Check if click is vertically within this animation's sprite area
  if (spriteY < topY || spriteY > topY + height) return;

  // Check if click is before the first frame
  if (spriteX < baseX) return;

  // Calculate which frame was clicked
  const offsetX = spriteX - baseX;
  const frameIndex = Math.floor(offsetX / range);
  const frameStartX = baseX + frameIndex * range;

  // Check if click is within this frame's rectangle (not in the gap)
  if (spriteX > frameStartX + width) return;

  // Check if this frame is within the valid limit
  if (frameIndex * range > limit) return;

  // Find the last frame's start offset
  const lastFrameOffset = Math.floor(limit / range) * range;

  // If this is already the last frame, do nothing
  if (frameIndex * range >= lastFrameOffset) return;

  // Prompt user to set sprite-limit to this frame's X start position
  const newLimit = frameIndex * range;
  const frameCount = frameIndex + 1;

  const confirmed = await showConfirmDialog({
    html: `Set sprite-limit to <strong>${newLimit}</strong>?<br>The animation will have <strong>${frameCount}</strong> frame(s).`
  });

  if (confirmed) {
    anim.spriteLimit = newLimit;

    // Update the DOM input field
    const cards = el.animationsList.querySelectorAll('.animation-card');
    if (cards[selectedAnimIndex]) {
      const limitInput = cards[selectedAnimIndex].querySelector('.anim-limit');
      if (limitInput) limitInput.value = newLimit;
    }

    // Update animation preview if active
    if (animPreviewState.anim === anim) {
      syncAnimPreview();
    }

    renderSpritesheet();
    updateJSONPreview();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIRM DIALOG
// ═══════════════════════════════════════════════════════════════════════════════

function showConfirmDialog(opts) {
  return new Promise((resolve) => {
    const overlay = $('confirmDialog');
    const messageEl = $('confirmDialogMessage');
    const btnConfirm = $('confirmDialogConfirm');
    const btnCancel = $('confirmDialogCancel');
    const btnClose = $('confirmDialogClose');

    // Accept either a plain string (backward-compatible) or an object with { title, html }
    const content = (typeof opts === 'string') ? opts : (opts.html || '');
    messageEl.innerHTML = content;
    overlay.style.display = 'flex';

    function cleanup() {
      overlay.style.display = 'none';
      btnConfirm.removeEventListener('click', onConfirm);
      btnCancel.removeEventListener('click', onCancel);
      btnClose.removeEventListener('click', onCancel);
      document.removeEventListener('keydown', onKeydown);
    }

    function onConfirm() {
      cleanup();
      resolve(true);
    }

    function onCancel() {
      cleanup();
      resolve(false);
    }

    function onKeydown(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
      if (e.key === 'Enter') {
        e.preventDefault();
        onConfirm();
      }
    }

    btnConfirm.addEventListener('click', onConfirm);
    btnCancel.addEventListener('click', onCancel);
    btnClose.addEventListener('click', onCancel);
    document.addEventListener('keydown', onKeydown);
  });
}

// ─── Check if preview is active for a given animation ─────────────────
function isPreviewActive(anim) {
  return animPreviewState.active && animPreviewState.anim && animPreviewState.anim.id === anim.id;
}

// ─── Toggle animation preview from eye button ─────────────────────────
function toggleAnimationPreview(anim) {
  if (!spritesheetImage || !anim.animated) return;

  if (isPreviewActive(anim)) {
    stopAnimationPreview();
  } else {
    showAnimationPreview(anim);
  }
}

// ─── Select animation by index (called from card click) ────────────────────
function selectAnimation(index) {
  if (index < 0 || index >= animations.length) return;
  selectedAnimIndex = index;
  if (spritesheetImage) {
    renderSpritesheet();
  }
}

// ─── Redraw spritesheet + sync animation preview ──────────────────────────
function refreshSpritesheet() {
  if (spritesheetImage) {
    renderSpritesheet();
    // Keep the animation preview in sync whenever the spritesheet overlays change
    syncAnimPreview();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANIMATION PREVIEW POPUP
// ═══════════════════════════════════════════════════════════════════════════════

let animPreviewState = {
  active: false,
  paused: false,
  animId: null,
  currentFrame: 0,
  totalFrames: 0,
  lastTime: 0,
  anim: null,
};

// Saved position for the animation preview popup (remembers drag position)
let animPreviewSavedPos = null;

const animPreviewEl = {
  popup:    $('animPreview'),
  title:    $('animPreviewTitle'),
  frame:    $('animPreviewFrame'),
  info:     $('animPreviewInfo'),
  canvas:   $('animPreviewCanvas'),
  btnClose: $('btnCloseAnimPreview'),
  btnToggle: $('btnToggleAnimPlay'),
};

function showAnimationPreview(anim) {
  if (!spritesheetImage || !anim.animated) return;
  if (anim.spriteRange <= 0) return;

  // Calculate frame count: (spriteLimit / spriteRange) + 1
  const frameCount = (anim.spriteLimit > 0 && anim.spriteRange > 0)
    ? Math.floor(anim.spriteLimit / anim.spriteRange) + 1
    : 1;

  if (frameCount <= 1) return;

  // Stop any existing preview
  stopAnimationPreview();

  // Initialize state
  animPreviewState.anim = anim;
  animPreviewState.totalFrames = frameCount;
  animPreviewState.currentFrame = 0;
  animPreviewState.lastTime = 0;
  animPreviewState.active = true;
  animPreviewState.paused = false;

  // Set canvas size to sprite dimensions
  const canvas = animPreviewEl.canvas;
  canvas.width = anim.spriteDirectionWidth;
  canvas.height = anim.spriteDirectionHeight;

  // Restore saved position if available, otherwise set default position
  animPreviewEl.popup.style.right = '';
  if (animPreviewSavedPos) {
    animPreviewEl.popup.style.left = animPreviewSavedPos.left;
    animPreviewEl.popup.style.top = animPreviewSavedPos.top;
  } else {
    animPreviewEl.popup.style.left = '20px';
    animPreviewEl.popup.style.top = '100px';
  }

  // Update UI
  animPreviewEl.title.textContent = `▶ ${anim.name}`;
  animPreviewEl.frame.textContent = `1/${frameCount}`;
  animPreviewEl.info.textContent = `${frameCount} frames × ${anim.speed}s | ${anim.loop ? 'loop 🔄' : 'once →'}`;
  animPreviewEl.popup.style.display = 'block';

  // Update toggle button icon
  updateToggleIcon();

  // Draw first frame
  drawAnimPreviewFrame(0);

  // Start animation loop
  animPreviewState.animId = requestAnimationFrame(animPreviewLoop);
}

function stopAnimationPreview() {
  animPreviewState.active = false;
  if (animPreviewState.animId) {
    cancelAnimationFrame(animPreviewState.animId);
    animPreviewState.animId = null;
  }
  animPreviewState.anim = null;
  animPreviewEl.popup.style.display = 'none';
}

function drawAnimPreviewFrame(frameIndex) {
  const anim = animPreviewState.anim;
  if (!anim || !spritesheetImage) return;

  const canvas = animPreviewEl.canvas;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const sx = anim.spriteDirectionLeft + (frameIndex * anim.spriteRange);
  const sy = anim.spriteDirectionTop;
  const sw = anim.spriteDirectionWidth;
  const sh = anim.spriteDirectionHeight;

  ctx.drawImage(spritesheetImage, sx, sy, sw, sh, 0, 0, sw, sh);

  animPreviewEl.frame.textContent = `${frameIndex + 1}/${animPreviewState.totalFrames}`;
}

function animPreviewLoop(timestamp) {
  if (!animPreviewState.active || !animPreviewState.anim) return;

  const anim = animPreviewState.anim;

  if (animPreviewState.paused) {
    // Keep requesting frames but don't advance
    animPreviewState.animId = requestAnimationFrame(animPreviewLoop);
    return;
  }

  if (animPreviewState.lastTime === 0) {
    animPreviewState.lastTime = timestamp;
  }

  const elapsed = timestamp - animPreviewState.lastTime;
  const frameDuration = anim.speed * 1000; // Convert seconds to ms

  if (elapsed >= frameDuration) {
    // Advance to next frame (keeping remainder for smooth timing)
    animPreviewState.lastTime = timestamp - (elapsed % frameDuration);
    animPreviewState.currentFrame++;

    if (animPreviewState.currentFrame >= animPreviewState.totalFrames) {
      if (anim.loop) {
        animPreviewState.currentFrame = 0;
      } else {
        // Stop at last frame
        animPreviewState.currentFrame = animPreviewState.totalFrames - 1;
        animPreviewState.active = false;
        drawAnimPreviewFrame(animPreviewState.currentFrame);
        return;
      }
    }

    drawAnimPreviewFrame(animPreviewState.currentFrame);
  }

  animPreviewState.animId = requestAnimationFrame(animPreviewLoop);
}

function toggleAnimPreviewPlay() {
  if (!animPreviewState.active) return;
  animPreviewState.paused = !animPreviewState.paused;
  if (!animPreviewState.paused) {
    animPreviewState.lastTime = 0; // Reset timing so it doesn't jump
  }
  updateToggleIcon();
}

function updateToggleIcon() {
  const btn = animPreviewEl.btnToggle;
  if (animPreviewState.paused) {
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M3 1v10l7-5z" fill="currentColor"/>
    </svg>`;
    btn.title = 'Play';
  } else {
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <rect x="2" y="1" width="3" height="10" rx="1" fill="currentColor"/>
      <rect x="7" y="1" width="3" height="10" rx="1" fill="currentColor"/>
    </svg>`;
    btn.title = 'Pause';
  }
}

// ─── Sync animation preview when animation properties change ──────────
function syncAnimPreview() {
  if (!animPreviewState.active || !animPreviewState.anim) return;

  const anim = animPreviewState.anim;

  // If animation is no longer animated or has no range, stop preview
  if (!anim.animated || anim.spriteRange <= 0) {
    stopAnimationPreview();
    renderAnimations(); // Update eye button state
    return;
  }

  // Recalculate frame count: (spriteLimit / spriteRange) + 1
  const newFrameCount = (anim.spriteLimit > 0 && anim.spriteRange > 0)
    ? Math.floor(anim.spriteLimit / anim.spriteRange) + 1
    : 1;

  if (newFrameCount <= 1) {
    stopAnimationPreview();
    renderAnimations(); // Update eye button state
    return;
  }

  // Resize canvas if sprite dimensions changed
  const canvas = animPreviewEl.canvas;
  canvas.width = anim.spriteDirectionWidth;
  canvas.height = anim.spriteDirectionHeight;

  // Adjust current frame if total frames changed
  if (newFrameCount !== animPreviewState.totalFrames) {
    animPreviewState.totalFrames = newFrameCount;
    if (animPreviewState.currentFrame >= newFrameCount) {
      animPreviewState.currentFrame = 0;
      animPreviewState.lastTime = 0; // Reset timing when jumping frames
    }
  }

  // Update title
  animPreviewEl.title.textContent = `▶ ${anim.name}`;

  // Update info text
  animPreviewEl.info.textContent = `${newFrameCount} frames × ${anim.speed}s | ${anim.loop ? 'loop 🔄' : 'once →'}`;

  // Redraw current frame with updated properties
  drawAnimPreviewFrame(animPreviewState.currentFrame);
}

// ─── Drag for Animation Preview Popup ─────────────────────────────────
let animPreviewDragData = null;

function startAnimPreviewDrag(e) {
  const rect = animPreviewEl.popup.getBoundingClientRect();
  // Clear right so it doesn't conflict with left positioning during drag
  animPreviewEl.popup.style.right = '';
  animPreviewDragData = {
    startX: e.clientX,
    startY: e.clientY,
    origLeft: rect.left,
    origTop: rect.top,
  };
  document.addEventListener('mousemove', onAnimPreviewDrag);
  document.addEventListener('mouseup', stopAnimPreviewDrag);
  e.preventDefault();
}

function onAnimPreviewDrag(e) {
  if (!animPreviewDragData) return;
  const dx = e.clientX - animPreviewDragData.startX;
  const dy = e.clientY - animPreviewDragData.startY;
  animPreviewEl.popup.style.left = (animPreviewDragData.origLeft + dx) + 'px';
  animPreviewEl.popup.style.top = (animPreviewDragData.origTop + dy) + 'px';
}

function stopAnimPreviewDrag() {
  if (animPreviewDragData) {
    // Save the current position so it persists across preview updates
    animPreviewSavedPos = {
      left: animPreviewEl.popup.style.left,
      top: animPreviewEl.popup.style.top,
    };
  }
  animPreviewDragData = null;
  document.removeEventListener('mousemove', onAnimPreviewDrag);
  document.removeEventListener('mouseup', stopAnimPreviewDrag);
}

// ─── Animation Preview Event Listeners ──────────────────────────────
animPreviewEl.btnClose.addEventListener('click', stopAnimationPreview);
animPreviewEl.btnToggle.addEventListener('click', toggleAnimPreviewPlay);
animPreviewEl.popup.addEventListener('mousedown', (e) => {
  // Only start drag if clicking on the header (not on controls)
  if (e.target.closest('.anim-preview-header') && !e.target.closest('.anim-preview-close') && !e.target.closest('.anim-preview-frame')) {
    startAnimPreviewDrag(e);
  }
});

// Close preview on Escape (already handled in shared Escape handler)

// ─── Spritesheet Event Listeners ──────────────────────────────────────────
spriteEl.btnLoad.addEventListener('click', openSpritesheet);
spriteEl.fileInput.addEventListener('change', handleSpritesheetLoad);
spriteEl.btnClose.addEventListener('click', closeSpritesheetModal);
spriteEl.btnZoomIn.addEventListener('click', zoomIn);
spriteEl.btnZoomOut.addEventListener('click', zoomOut);
spriteEl.canvas.addEventListener('mousemove', onCanvasMouseMove);
spriteEl.canvas.addEventListener('mouseleave', onCanvasMouseLeave);
spriteEl.canvas.addEventListener('click', onCanvasClick);
// Empty state load button and inline load button
if (spriteEl.btnEmptyLoad) {
  spriteEl.btnEmptyLoad.addEventListener('click', openSpritesheet);
}
if (spriteEl.btnLoadInline) {
  spriteEl.btnLoadInline.addEventListener('click', openSpritesheet);
}
// Drag & drop on spritesheet panel
spriteEl.modal.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.stopPropagation();
  spriteEl.modal.classList.add('sprite-panel-dragover');
});
spriteEl.modal.addEventListener('dragleave', (e) => {
  e.preventDefault();
  e.stopPropagation();
  spriteEl.modal.classList.remove('sprite-panel-dragover');
});
spriteEl.modal.addEventListener('drop', (e) => {
  e.preventDefault();
  e.stopPropagation();
  spriteEl.modal.classList.remove('sprite-panel-dragover');
  const file = e.dataTransfer.files[0];
  if (!file) return;
  const acceptedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/bmp'];
  if (!acceptedTypes.some(t => file.type.startsWith(t.split('/')[0]))) return;
  // Create a synthetic event for handleSpritesheetLoad
  const syntheticEvent = { target: { files: [file], value: '' } };
  handleSpritesheetLoad(syntheticEvent);
});

// ─── Event Listeners ─────────────────────────────────────────────────────────
// Form inputs
el.texturename.addEventListener('input', () => {
  updateJSONPreview();
});

el.texturename.addEventListener('change', () => {
  autoLoadSpritesheet();
});

[el.lightR, el.lightG, el.lightB, el.lightA].forEach(input => {
  input.addEventListener('input', () => {
    updateColorPreview();
    updateJSONPreview();
  });
});

[el.propGeneration, el.textureOriginalChance, el.front, el.lightRange, el.lightIntensity, el.trailFreq].forEach(input => {
  input.addEventListener('input', updateJSONPreview);
});

// Dimension fields also refresh the spritesheet (green dimension rectangle overlay)
[el.dimWidth, el.dimHeight].forEach(input => {
  input.addEventListener('input', () => {
    updateJSONPreview();
    refreshSpritesheet();
  });
});

// Buttons
el.btnAddAnimation.addEventListener('click', () => {
  // Copy from last animation, stacking as a new row
  if (animations.length > 0) {
    const last = animations[animations.length - 1];
    addAnimation({
      name: 'new-animation',
      spriteDirectionLeft: last.spriteDirectionLeft,
      spriteDirectionTop: last.spriteDirectionTop + last.spriteDirectionHeight,
      spriteDirectionWidth: last.spriteDirectionWidth,
      spriteDirectionHeight: last.spriteDirectionHeight,
      spriteLimit: last.spriteLimit,
      spriteRange: last.spriteRange,
      animated: last.animated,
      reverseMode: last.reverseMode,
      loop: last.loop,
      sideFlip: last.sideFlip,
      speed: last.speed,
      sound: last.sound,
    });
  } else {
    // No existing animations, use default
    addAnimation({ name: 'new-animation' });
  }
});

el.btnOpen.addEventListener('click', openFile);
el.fileInput.addEventListener('change', handleFileOpen);
el.btnSave.addEventListener('click', saveFile);
el.btnCopy.addEventListener('click', copyJSON);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl+O / Cmd+O -> Open
  if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
    e.preventDefault();
    openFile();
  }
  // Ctrl+S / Cmd+S -> Save
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    saveFile();
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// LOCALSTORAGE FILE VAULT — Firefox-compatible file management
// ═══════════════════════════════════════════════════════════════════════════════

// The vault stores JSON files in localStorage organized in a folder-like structure.
// Structure: { "folders": { "folderName": true }, "files": { "folderName/filename.json": { content, createdAt, updatedAt } } }

const VAULT_KEY = 'duq_sprite_vault';

function _getVault() {
  try {
    const raw = localStorage.getItem(VAULT_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && parsed.folders && parsed.files) {
        return parsed;
      }
    }
  } catch (e) { /* ignore */ }
  // Default vault structure
  return { folders: { 'My Sprites': true }, files: {} };
}

function _saveVault(vault) {
  try {
    localStorage.setItem(VAULT_KEY, JSON.stringify(vault));
  } catch (e) {
    // localStorage might be full — warn user
    showNotification('Could not save to vault. Storage may be full.', 'error');
  }
}

// ─── Vault Folder Management ────────────────────────────────────────────────

function getVaultFolders() {
  const vault = _getVault();
  return Object.keys(vault.folders).sort();
}

function createVaultFolder(name) {
  name = name.trim();
  if (!name) return false;
  const vault = _getVault();
  if (vault.folders[name]) return false; // Already exists
  vault.folders[name] = true;
  _saveVault(vault);
  return true;
}

function deleteVaultFolder(name) {
  const vault = _getVault();
  if (!vault.folders[name]) return false;
  // Delete all files in this folder
  const prefix = name + '/';
  Object.keys(vault.files).forEach(key => {
    if (key.startsWith(prefix)) {
      delete vault.files[key];
    }
  });
  delete vault.folders[name];
  _saveVault(vault);
  return true;
}

function renameVaultFolder(oldName, newName) {
  newName = newName.trim();
  if (!newName || oldName === newName) return false;
  const vault = _getVault();
  if (!vault.folders[oldName]) return false;
  if (vault.folders[newName]) return false; // Already exists

  // Rename folder
  delete vault.folders[oldName];
  vault.folders[newName] = true;

  // Move all files from old folder to new folder
  const prefix = oldName + '/';
  const filesToMove = {};
  Object.keys(vault.files).forEach(key => {
    if (key.startsWith(prefix)) {
      const newKey = newName + '/' + key.slice(prefix.length);
      filesToMove[newKey] = vault.files[key];
      delete vault.files[key];
    }
  });
  Object.assign(vault.files, filesToMove);

  _saveVault(vault);
  return true;
}

// ─── Vault File Management ──────────────────────────────────────────────────

function getVaultFiles(folderName) {
  const vault = _getVault();
  const prefix = folderName + '/';
  const result = [];
  Object.keys(vault.files).forEach(key => {
    if (key.startsWith(prefix)) {
      const fileData = vault.files[key];
      result.push({
        key: key,
        name: key.slice(prefix.length),
        content: fileData.content,
        createdAt: fileData.createdAt,
        updatedAt: fileData.updatedAt,
      });
    }
  });
  // Sort by name
  result.sort((a, b) => a.name.localeCompare(b.name));
  return result;
}

function getAllVaultFiles() {
  const vault = _getVault();
  const result = [];
  Object.keys(vault.files).forEach(key => {
    const fileData = vault.files[key];
    const slashIdx = key.indexOf('/');
    const folder = slashIdx > -1 ? key.slice(0, slashIdx) : '';
    const name = slashIdx > -1 ? key.slice(slashIdx + 1) : key;
    result.push({
      key: key,
      folder: folder,
      name: name,
      content: fileData.content,
      createdAt: fileData.createdAt,
      updatedAt: fileData.updatedAt,
    });
  });
  result.sort((a, b) => a.folder.localeCompare(b.folder) || a.name.localeCompare(b.name));
  return result;
}

function saveJsonToVault(folderName, fileName, jsonContent) {
  const vault = _getVault();
  if (!vault.folders[folderName]) return false;
  const key = folderName + '/' + fileName;
  const now = new Date().toISOString();
  if (vault.files[key]) {
    vault.files[key].content = jsonContent;
    vault.files[key].updatedAt = now;
  } else {
    vault.files[key] = {
      content: jsonContent,
      createdAt: now,
      updatedAt: now,
    };
  }
  _saveVault(vault);
  return true;
}

function loadJsonFromVault(key) {
  const vault = _getVault();
  const fileData = vault.files[key];
  if (!fileData) return null;
  return fileData.content;
}

function deleteVaultFile(key) {
  const vault = _getVault();
  if (!vault.files[key]) return false;
  delete vault.files[key];
  _saveVault(vault);
  return true;
}

function getVaultStorageInfo() {
  // Estimate storage usage
  try {
    const raw = localStorage.getItem(VAULT_KEY) || '{}';
    const bytes = new Blob([raw]).size;
    const limit = 5 * 1024 * 1024; // ~5MB typical localStorage limit
    return { used: bytes, limit: limit, percent: Math.round((bytes / limit) * 100) };
  } catch (e) {
    return { used: 0, limit: 5242880, percent: 0 };
  }
}

// ─── Render Vault Manager UI ─────────────────────────────────────────────────

function renderVaultManager() {
  const container = $('vaultManager');
  if (!container) return;
  
  const folders = getVaultFolders();
  const selectedFolder = container.dataset.selectedFolder || folders[0] || '';
  
  let html = '<div class="vault-layout">';
  
  // Left sidebar: folder list
  html += '<div class="vault-sidebar">';
  html += '<div class="vault-sidebar-header">';
  html += '<span>Folders</span>';
  html += '<button class="btn btn-sm btn-outline" id="btnVaultNewFolder" title="New folder">+</button>';
  html += '</div>';
  html += '<div class="vault-folder-list">';
  
  if (folders.length === 0) {
    html += '<div class="vault-empty">No folders. Create one!</div>';
  } else {
    folders.forEach(f => {
      const active = f === selectedFolder ? ' vault-folder-active' : '';
      html += `<div class="vault-folder${active}" data-folder="${escapeHtml(f)}">`;
      html += `<span class="vault-folder-icon">📁</span>`;
      html += `<span class="vault-folder-name">${escapeHtml(f)}</span>`;
      html += `<span class="vault-folder-count">(${getVaultFiles(f).length})</span>`;
      html += `<button class="vault-folder-rename" title="Rename folder">✏️</button>`;
      html += `<button class="vault-folder-delete" title="Delete folder">🗑️</button>`;
      html += '</div>';
    });
  }
  
  html += '</div>'; // .vault-folder-list
  html += '</div>'; // .vault-sidebar
  
  // Right side: file list for selected folder
  html += '<div class="vault-content">';
  html += '<div class="vault-content-header">';
  html += `<span class="vault-current-folder">${escapeHtml(selectedFolder)}</span>`;
  html += '<div class="vault-content-actions">';
  html += '<button class="btn btn-sm btn-outline" id="btnVaultImportFile" title="Import JSON file from computer">📥 Import</button>';
  html += '<button class="btn btn-sm btn-outline" id="btnVaultSaveCurrent" title="Save current editor state to vault">💾 Save Current</button>';
  html += '</div>';
  html += '</div>';
  
  const files = getVaultFiles(selectedFolder);
  html += '<div class="vault-file-list">';
  
  if (files.length === 0) {
    html += '<div class="vault-empty">No files in this folder.</div>';
  } else {
    files.forEach(file => {
      const date = new Date(file.updatedAt);
      const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      html += `<div class="vault-file-item" data-key="${escapeHtml(file.key)}">`;
      html += `<span class="vault-file-icon">📄</span>`;
      html += '<div class="vault-file-info">';
      html += `<span class="vault-file-name">${escapeHtml(file.name)}</span>`;
      html += `<span class="vault-file-meta">${dateStr}</span>`;
      html += '</div>';
      html += `<button class="vault-file-open" title="Open this file">▶ Open</button>`;
      html += `<button class="vault-file-delete" title="Delete">🗑️</button>`;
      html += '</div>';
    });
  }
  
  html += '</div>'; // .vault-file-list
  
  // Storage info
  const info = getVaultStorageInfo();
  const barColor = info.percent > 80 ? 'var(--danger)' : info.percent > 50 ? 'var(--warning)' : 'var(--accent)';
  html += '<div class="vault-storage-info">';
  html += `<div class="vault-storage-bar"><div class="vault-storage-fill" style="width:${info.percent}%;background:${barColor}"></div></div>`;
  html += `<span class="vault-storage-text">${formatFileSize(info.used)} / ${formatFileSize(info.limit)}</span>`;
  html += '</div>';
  
  html += '</div>'; // .vault-content
  html += '</div>'; // .vault-layout
  
  container.innerHTML = html;
  container.dataset.selectedFolder = selectedFolder;
  
  // Wire up events
  _wireVaultEvents();
}

function _wireVaultEvents() {
  // Folder selection
  document.querySelectorAll('.vault-folder').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.closest('.vault-folder-rename') || e.target.closest('.vault-folder-delete')) return;
      const container = $('vaultManager');
      container.dataset.selectedFolder = el.dataset.folder;
      renderVaultManager();
    });
  });

  // New folder
  const btnNew = $('btnVaultNewFolder');
  if (btnNew) {
    btnNew.addEventListener('click', async () => {
      const name = prompt('Enter folder name:');
      if (name && name.trim()) {
        if (createVaultFolder(name.trim())) {
          const container = $('vaultManager');
          container.dataset.selectedFolder = name.trim();
          renderVaultManager();
        } else {
          alert('Folder already exists or invalid name.');
        }
      }
    });
  }

  // Rename folder
  document.querySelectorAll('.vault-folder-rename').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const folderEl = btn.closest('.vault-folder');
      const oldName = folderEl.dataset.folder;
      const newName = prompt('Rename folder to:', oldName);
      if (newName && newName.trim() && newName.trim() !== oldName) {
        if (renameVaultFolder(oldName, newName.trim())) {
          const container = $('vaultManager');
          container.dataset.selectedFolder = newName.trim();
          renderVaultManager();
        } else {
          alert('Could not rename folder.');
        }
      }
    });
  });

  // Delete folder
  document.querySelectorAll('.vault-folder-delete').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const folderEl = btn.closest('.vault-folder');
      const folderName = folderEl.dataset.folder;
      const confirmed = await showConfirmDialog({
        html: `Delete folder "<strong>${escapeHtml(folderName)}</strong>" and all files inside?`
      });
      if (confirmed) {
        deleteVaultFolder(folderName);
        const container = $('vaultManager');
        const folders = getVaultFolders();
        container.dataset.selectedFolder = folders[0] || '';
        renderVaultManager();
      }
    });
  });

  // Open file
  document.querySelectorAll('.vault-file-open').forEach(btn => {
    btn.addEventListener('click', function() {
      const fileItem = this.closest('.vault-file-item');
      const key = fileItem.dataset.key;
      const jsonContent = loadJsonFromVault(key);
      if (jsonContent) {
        try {
          const data = JSON.parse(jsonContent);
          loadFromJSON(data);
          showNotification('Loaded: ' + key, 'success');
          // Close the JSON files popup
          const popup = $('jsonFilesPopup');
          if (popup) popup.style.display = 'none';
        } catch (err) {
          alert('Error parsing JSON: ' + err.message);
        }
      }
    });
  });

  // Delete file
  document.querySelectorAll('.vault-file-delete').forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.stopPropagation();
      const fileItem = this.closest('.vault-file-item');
      const key = fileItem.dataset.key;
      const confirmed = await showConfirmDialog({
        html: `Delete "<strong>${escapeHtml(key)}</strong>"?`
      });
      if (confirmed) {
        deleteVaultFile(key);
        renderVaultManager();
      }
    });
  });

  // Import file
  const btnImport = $('btnVaultImportFile');
  if (btnImport) {
    btnImport.addEventListener('click', () => {
      // Create a hidden file input
      let importInput = $('vaultImportInput');
      if (!importInput) {
        importInput = document.createElement('input');
        importInput.type = 'file';
        importInput.id = 'vaultImportInput';
        importInput.accept = '.json';
        importInput.style.display = 'none';
        document.body.appendChild(importInput);
      }
      importInput.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const container = $('vaultManager');
        const folder = container.dataset.selectedFolder || 'My Sprites';
        const reader = new FileReader();
        reader.onload = function(ev) {
          const content = ev.target.result;
          // Validate it's valid JSON
          try {
            JSON.parse(content);
          } catch (err) {
            alert('Invalid JSON file: ' + err.message);
            return;
          }
          // Use original filename or prompt
          let fileName = file.name;
          if (!fileName.endsWith('.json')) fileName += '.json';
          saveJsonToVault(folder, fileName, content);
          renderVaultManager();
          showNotification('Imported: ' + fileName, 'success');
        };
        reader.readAsText(file);
        this.value = '';
      };
      importInput.click();
    });
  }

  // Save current
  const btnSaveCurrent = $('btnVaultSaveCurrent');
  if (btnSaveCurrent) {
    btnSaveCurrent.addEventListener('click', () => {
      syncAllAnimations();
      const data = buildJSON();
      if (!data.texturename) {
        alert('Set a texture name before saving.');
        return;
      }
      const container = $('vaultManager');
      const folder = container.dataset.selectedFolder || 'My Sprites';
      const fileName = (data.texturename || 'sprite').replace(/[\/\\]/g, '_') + '.json';
      const jsonContent = JSON.stringify(data, null, 4);
      
      saveJsonToVault(folder, fileName, jsonContent);
      renderVaultManager();
      showNotification('Saved to vault: ' + folder + '/' + fileName, 'success');
    });
  }
}

// ─── Format file size helper ─────────────────────────────────────────────────
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ═══════════════════════════════════════════════════════════════════════════════
// PROJECT & PREFERENCES DROPDOWN MENU
// ═══════════════════════════════════════════════════════════════════════════════

// ─── localStorage Keys ────────────────────────────────────────────────────────
const STORAGE_KEY_RECENT = 'duq_recent_projects';
const STORAGE_KEY_CURRENT = 'duq_current_project';
const STORAGE_KEY_PROJECT_PATH = 'duq_project_full_path';

// ─── IndexedDB — Persistent Directory Handle ─────────────────────────────────
// The File System Access API handles can be stored in IndexedDB so they survive
// page reloads (Chrome 86+).

const IDB_NAME = 'duq_sprite_editor';
const IDB_VERSION = 1;
const IDB_STORE = 'handles';

function openHandleDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(IDB_NAME, IDB_VERSION);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(IDB_STORE)) {
        db.createObjectStore(IDB_STORE);
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveDirHandleToIDB(handle) {
  try {
    const db = await openHandleDB();
    const tx = db.transaction(IDB_STORE, 'readwrite');
    tx.objectStore(IDB_STORE).put(handle, 'projectDir');
    return new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch (err) {
    console.warn('Could not save handle to IndexedDB:', err);
  }
}

async function loadDirHandleFromIDB() {
  try {
    const db = await openHandleDB();
    const tx = db.transaction(IDB_STORE, 'readonly');
    const request = tx.objectStore(IDB_STORE).get('projectDir');
    return new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  } catch (err) {
    console.warn('Could not restore project directory handle:', err);
    return null;
  }
}

// ─── Project State ───────────────────────────────────────────────────────────
let currentProject = null;
let projectSetupRequired = false;
let projectDirHandle = null;        // FileSystemDirectoryHandle for project root
let texturesDirHandle = null;       // Cached FileSystemDirectoryHandle for <root>/data/textures
let projectFullPath = '';           // User-provided full path for display (localStorage)

// ─── DOM References ──────────────────────────────────────────────────────────
const dropdown = $('prefDropdown');
const btnGear = $('btnPreferences');
const projectFileInput = $('projectFileInput');

const menuEl = {
  projectName:  $('menuProjectName'),
  statusDot:    $('menuStatusDot'),
  dirName:      $('menuDirName'),
  recentList:   $('menuRecentList'),
  btnSetDir:    $('menuSetDir'),
  btnOpen:      $('menuOpenProject'),
  btnSave:      $('menuSaveProject'),
  btnClear:     $('menuClearRecent'),
  btnJsonFiles: $('menuJsonFiles'),
  jsonBadge:    $('menuJsonBadge'),
};

// ─── JSON Files Popup DOM ────────────────────────────────────────────────────
const jsonPopup = $('jsonFilesPopup');
const jsonPopupDir = $('jsonPopupDir');
const jsonFilesList = $('jsonFilesList');
const jsonFilesCount = $('jsonFilesCount');
const btnCloseJsonPopup = $('btnCloseJsonPopup');
const btnRefreshJsonFiles = $('btnRefreshJsonFiles');

// ─── Build project data from current editor state ────────────────────────────
function buildProjectData() {
  syncAllAnimations();
  const jsonData = buildJSON();
  return {
    version: 1,
    name: getProjectNameForSave(),
    createdAt: currentProject?.createdAt || new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    editorState: {
      jsonData: jsonData,
      spritesheetFilename: spritesheetFilename || '',
    },
  };
}

function getProjectNameForSave() {
  if (currentProject) return currentProject.name;
  // Use texture name as fallback
  const tn = el.texturename.value.trim();
  return tn || 'My Project';
}

// ─── Load project data into editor ───────────────────────────────────────────
function loadProjectData(projectData, projectPath) {
  if (!projectData || !projectData.editorState) return;

  const state = projectData.editorState;
  if (state.jsonData) {
    loadFromJSON(state.jsonData);
  }

  currentProject = {
    name: projectData.name || 'My Project',
    path: projectPath || '',
    createdAt: projectData.createdAt,
    updatedAt: projectData.updatedAt,
  };

  updateProjectStatus(true, currentProject.path || currentProject.name || 'Project loaded');
  addToRecentProjects(projectData, projectPath || '');
  finishProjectSetup();
}

// ─── Finish project setup (close required mode) ──────────────────────────────
function finishProjectSetup() {
  if (projectSetupRequired) {
    projectSetupRequired = false;
    closeDropdown();
  }
}

// ─── Update dropdown project info ────────────────────────────────────────────
function updateProjectStatus(active, message) {
  menuEl.statusDot.className = 'status-dot' + (active ? ' status-dot-active' : ' status-dot-idle');
  menuEl.projectName.textContent = message || 'No project';
  updateDirDisplay();
}

function updateDirDisplay() {
  if (projectFullPath) {
    menuEl.dirName.textContent = projectFullPath;
  } else if (projectDirHandle) {
    menuEl.dirName.textContent = projectDirHandle.name;
  } else {
    menuEl.dirName.textContent = '';
  }
}

function getProjectDisplayPath() {
  // Returns the best available path for display purposes
  if (projectFullPath) return projectFullPath;
  if (projectDirHandle) return projectDirHandle.name;
  return '';
}

// ─── File System Access API — Project Directory ──────────────────────────────
// Uses the modern File System Access API (Chrome 86+, Edge 86+)
// to let the user pick a project root folder and default to <root>/data/textures/

async function setupProjectDirectory() {
  try {
    if (!('showDirectoryPicker' in window)) {
      // Firefox / unsupported browser — use localStorage vault instead
      showNotification('Folder selection not supported in this browser. Use the "Project JSON Files" vault (⚙️ > Project JSON Files) to manage files in localStorage.', 'success');
      openJsonFilesPopup();
      return;
    }
    projectDirHandle = await window.showDirectoryPicker({ mode: 'readwrite' });
    texturesDirHandle = null; // Reset cache — will be re-resolved on next open/save
    updateDirDisplay();

    // Persist the handle in IndexedDB so it survives page reload
    await saveDirHandleToIDB(projectDirHandle);

    try {
      localStorage.setItem('duq_project_dir', projectDirHandle.name);
    } catch { /* ignore */ }
  } catch (err) {
    if (err.name !== 'AbortError' && err.name !== 'SecurityError') {
      console.warn('Error selecting directory:', err);
    }
  }
}

async function getTexturesDirHandle() {
  if (!projectDirHandle) return null;
  if (texturesDirHandle) return texturesDirHandle;

  try {
    // Try to get existing data/textures directory
    let dir = await projectDirHandle.getDirectoryHandle('data');
    dir = await dir.getDirectoryHandle('textures');
    texturesDirHandle = dir;
    return texturesDirHandle;
  } catch {
    // data/textures doesn't exist — try to create it
    try {
      let dir = await projectDirHandle.getDirectoryHandle('data', { create: true });
      dir = await dir.getDirectoryHandle('textures', { create: true });
      texturesDirHandle = dir;
      return texturesDirHandle;
    } catch (err) {
      console.warn('Could not access/create data/textures:', err);
      return null;
    }
  }
}

// ─── Auto-load Spritesheet from resources/sprites/<texturename> ──────────────
// After loading a JSON, tries to find and load the matching sprite sheet at
// <project>/resources/sprites/<texturename> with common image extensions.
// The FIRST attempt always tries <texturename>.png at the exact expected path.
// Only if .png is not found, it falls back to trying other extensions.

const SPRITESHEET_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'];

async function autoLoadSpritesheet() {
  let tn = el.texturename.value.trim();
  if (!tn) return;

  // Normalize path separators — replace Windows backslashes with forward slashes
  tn = tn.replace(/\\/g, '/');

  // Build the full expected path: <project>/resources/sprites/<texturename>.png
  // Uses the user-provided full path from the menu when available
  const projectDirName = getProjectDisplayPath();
  const projectPrefix = projectDirName ? projectDirName + '/' : '';
  const displayPath = projectPrefix + 'resources/sprites/' + tn + '.png';

  if (!projectDirHandle) {
    showNotification(
      'Spritesheet not found — set the project directory (⚙️ > Set Project Directory). Expected path: ' + displayPath
    );
    return;
  }

  // ── Shared helper to navigate into a "resources/sprites/..." subdirectory tree ──
  // Given a starting directory handle, navigates through resources/sprites/
  // and the sub-path segments of texturename. Returns { dir, filenameBase, ok }.
  async function navigateToSpriteDir(startDir) {
    try {
      let dir = startDir;
      dir = await dir.getDirectoryHandle('resources');
      dir = await dir.getDirectoryHandle('sprites');

      const parts = tn.split('/');
      const filenameBase = parts.pop();
      for (const segment of parts) {
        dir = await dir.getDirectoryHandle(segment);
      }

      return { dir, filenameBase, ok: true };
    } catch {
      return { ok: false };
    }
  }

  // ── Helper: try to load a specific extension from a directory ──
  async function tryLoadExtension(dir, filenameBase, ext) {
    try {
      const fh = await dir.getFileHandle(filenameBase + ext);
      const file = await fh.getFile();
      const dataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
      });
      const img = await new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error('Failed to decode image'));
        img.src = dataUrl;
      });
      spritesheetImage = img;
      spritesheetFilename = filenameBase + ext;
      spriteZoom = 1;
      showSpritesheetModal();
      renderSpritesheet();
      return true;
    } catch {
      return false;
    }
  }

  try {
    // ─── FIRST ATTEMPT: Try only .png at the exact expected path ───
    const nav = await navigateToSpriteDir(projectDirHandle);
    if (nav.ok) {
      const pngLoaded = await tryLoadExtension(nav.dir, nav.filenameBase, '.png');
      if (pngLoaded) return;
    }

    // ─── SECOND ATTEMPT: Try all other extensions in the same directory ───
    if (nav.ok) {
      for (const ext of SPRITESHEET_EXTENSIONS) {
        if (ext === '.png') continue; // Already tried .png above
        const loaded = await tryLoadExtension(nav.dir, nav.filenameBase, ext);
        if (loaded) return;
      }
    }

    // ─── THIRD ATTEMPT: Fallback — navigate up from JSON file location ───
    if (lastOpenedJsonHandle) {
      try {
        // getParent() is available in Chrome 122+ (File System Access API)
        // Navigate up: <root>/data/textures/file.json  →  <root>/resources/sprites/
        const jsonDir  = await lastOpenedJsonHandle.getParent();  // data/textures/
        const dataDir  = await jsonDir.getParent();              // data/
        const rootDir  = await dataDir.getParent();              // <root>/

        const fallbackNav = await navigateToSpriteDir(rootDir);
        if (fallbackNav.ok) {
          const pngLoaded = await tryLoadExtension(fallbackNav.dir, fallbackNav.filenameBase, '.png');
          if (pngLoaded) return;

          for (const ext of SPRITESHEET_EXTENSIONS) {
            if (ext === '.png') continue;
            const loaded = await tryLoadExtension(fallbackNav.dir, fallbackNav.filenameBase, ext);
            if (loaded) return;
          }
        }
      } catch {
        // Fallback path failed — continue to notification
      }
    }

    // No matching file found for any extension
    showNotification(
      'Spritesheet file not found: ' + displayPath +
      ' (extensions: ' + SPRITESHEET_EXTENSIONS.join(', ') + ')'
    );
  } catch (err) {
    showNotification('Error loading spritesheet: ' + err.message + ' — ' + displayPath);
  }
}

// ─── Save Project As (download .duq-project file) ────────────────────────────
function saveProjectAs() {
  const projectData = buildProjectData();
  const json = JSON.stringify(projectData, null, 4);
  const filename = (projectData.name || 'project').replace(/[\/\\\s]/g, '_') + '.duq-project';

  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);

  currentProject = {
    name: projectData.name,
    path: filename,
    createdAt: projectData.createdAt,
    updatedAt: projectData.updatedAt,
  };

  updateProjectStatus(true, filename);
  saveCurrentProjectToStorage();
  addToRecentProjects(projectData, filename);
  finishProjectSetup();

  // Feedback on save button
  const original = menuEl.btnSave.innerHTML;
  menuEl.btnSave.innerHTML = `<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2 1v12h10V4.5L8.5 1H2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
    <path d="M4 8h6v4H4V8z" stroke="currentColor" stroke-width="1.5" fill="none"/>
  </svg> ✓ Saved!`;
  setTimeout(() => { menuEl.btnSave.innerHTML = original; }, 1500);
}

// ─── Open Project File ───────────────────────────────────────────────────────
function openProjectFile() {
  projectFileInput.click();
}

function handleProjectFileOpen(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      loadProjectData(data, file.name);
      closeDropdown();
    } catch (err) {
      alert('Error reading project file: ' + err.message);
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ─── Recent Projects (localStorage) ──────────────────────────────────────────
function getRecentProjects() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY_RECENT);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function addToRecentProjects(projectData, path) {
  const recent = getRecentProjects();
  const name = projectData.name || 'My Project';
  const existingIndex = recent.findIndex(p => p.path === path && path !== '');
  if (existingIndex !== -1) recent.splice(existingIndex, 1);

  recent.unshift({
    name, path, lastOpened: new Date().toISOString(),
    data: projectData,
  });

  if (recent.length > 10) recent.pop();
  localStorage.setItem(STORAGE_KEY_RECENT, JSON.stringify(recent));
  renderRecentProjects();
}

function renderRecentProjects() {
  const recent = getRecentProjects();
  const list = menuEl.recentList;

  if (recent.length === 0) {
    list.innerHTML = '<div class="pref-menu-empty">No recent projects.</div>';
    return;
  }

  list.innerHTML = recent.map((item, i) => {
    const date = new Date(item.lastOpened);
    const dateStr = date.toLocaleDateString('en-US', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
    return `
      <div class="pref-menu-recent-item" data-index="${i}">
        <div class="pref-menu-recent-info">
          <span class="pref-menu-recent-name">${escapeHtml(item.name)}</span>
          <span class="pref-menu-recent-meta">${escapeHtml(item.path || '(in memory)')} — ${dateStr}</span>
        </div>
        <span class="pref-menu-recent-arrow">→</span>
      </div>
    `;
  }).join('');

  list.querySelectorAll('.pref-menu-recent-item').forEach(el => {
    el.addEventListener('click', async () => {
      const i = parseInt(el.dataset.index);
      const recent = getRecentProjects();
      const item = recent[i];
      if (!item || !item.data) return;

      // Try to open the actual .json file from disk via File System Access API
      const texturename = item.data?.editorState?.jsonData?.texturename;
      if (texturename && projectDirHandle) {
        try {
          const texturesDir = await getTexturesDirHandle();
          if (texturesDir) {
            const filename = texturename.replace(/[\/\\]/g, '_') + '.json';
            try {
              const fileHandle = await texturesDir.getFileHandle(filename);
              const file = await fileHandle.getFile();
              const text = await file.text();
              const jsonData = JSON.parse(text);
              loadFromJSON(jsonData);
              closeDropdown();
              return;
            } catch {
              // File not found on disk, fall through to stored data
            }
          }
        } catch {
          // Error accessing textures dir, fall through
        }
      }

      // Fallback: load from stored data
      loadProjectData(item.data, item.path);
      closeDropdown();
    });
  });
}

function clearRecentProjects() {
  if (confirm('Are you sure you want to clear the recent projects list?')) {
    localStorage.removeItem(STORAGE_KEY_RECENT);
    renderRecentProjects();
  }
}

// ─── Current Project (localStorage) ──────────────────────────────────────────
function saveCurrentProjectToStorage() {
  if (!currentProject) return;
  const data = {
    name: currentProject.name,
    path: currentProject.path,
    createdAt: currentProject.createdAt,
    updatedAt: currentProject.updatedAt,
    editorState: {
      jsonData: buildJSON(),
      spritesheetFilename: spritesheetFilename || '',
    },
  };
  localStorage.setItem(STORAGE_KEY_CURRENT, JSON.stringify(data));
}

function loadCurrentProjectFromStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY_CURRENT);
    if (stored) {
      const data = JSON.parse(stored);
      if (data && data.editorState) {
        loadProjectData(data, data.path || '');
        return true;
      }
    }
  } catch { /* ignore */ }
  return false;
}

// ─── Dropdown Menu Logic ─────────────────────────────────────────────────────
function toggleDropdown(forceShow) {
  const isVisible = dropdown.classList.contains('visible');
  if (forceShow === true || (forceShow === undefined && !isVisible)) {
    showDropdown();
  } else {
    closeDropdown();
  }
}

function showDropdown() {
  renderRecentProjects();
  dropdown.classList.add('visible');
  btnGear.classList.add('active');

  if (projectSetupRequired) {
    dropdown.classList.add('required');
  }

  // Silently update JSON file count badge from vault
  try {
    const allFiles = getAllVaultFiles();
    if (allFiles.length > 0) {
      menuEl.jsonBadge.textContent = String(allFiles.length);
    }
  } catch (e) { /* ignore */ }
}

function closeDropdown() {
  if (projectSetupRequired) return;
  dropdown.classList.remove('visible', 'required');
  btnGear.classList.remove('active');
}

// ─── Event Listeners ─────────────────────────────────────────────────────────
btnGear.addEventListener('click', (e) => {
  e.stopPropagation();
  toggleDropdown();
});

// Close dropdown on outside click
document.addEventListener('click', (e) => {
  const wrapper = $('prefMenuWrapper');
  if (wrapper && !wrapper.contains(e.target)) {
    closeDropdown();
  }
});

// Menu actions
menuEl.btnSetDir.addEventListener('click', (e) => {
  e.stopPropagation();
  setupProjectDirectory();
});

menuEl.btnOpen.addEventListener('click', (e) => {
  e.stopPropagation();
  openProjectFile();
});

menuEl.btnSave.addEventListener('click', (e) => {
  e.stopPropagation();
  saveProjectAs();
});

menuEl.btnClear.addEventListener('click', (e) => {
  e.stopPropagation();
  clearRecentProjects();
});

projectFileInput.addEventListener('change', handleProjectFileOpen);

// ─── Project Path Input ──────────────────────────────────────────────────────
const projectPathInput = $('menuProjectPath');
if (projectPathInput) {
  projectPathInput.addEventListener('change', () => {
    let val = projectPathInput.value.trim();
    // Normalize backslashes to forward slashes for display consistency
    val = val.replace(/\\/g, '/');
    projectPathInput.value = val;
    projectFullPath = val;
    try {
      localStorage.setItem(STORAGE_KEY_PROJECT_PATH, val);
    } catch { /* ignore */ }
    updateDirDisplay();
  });
  // Also save on blur (when clicking outside)
  projectPathInput.addEventListener('blur', () => {
    let val = projectPathInput.value.trim();
    // Normalize backslashes to forward slashes for display consistency
    val = val.replace(/\\/g, '/');
    projectPathInput.value = val;
    if (val !== projectFullPath) {
      projectFullPath = val;
      try {
        localStorage.setItem(STORAGE_KEY_PROJECT_PATH, val);
      } catch { /* ignore */ }
      updateDirDisplay();
    }
  });
}

// ─── JSON Files Popup Logic (localStorage Vault) ─────────────────────────────
// This uses the localStorage vault instead of File System Access API,
// making it compatible with Firefox and all browsers.

function openJsonFilesPopup() {
  closeDropdown();

  // Show popup
  jsonPopup.style.display = 'flex';
  jsonPopupDir.textContent = 'localStorage Vault';

  // Render the vault manager inside the popup
  jsonFilesList.innerHTML = '<div id="vaultManager" class="vault-manager"></div>';
  jsonFilesCount.textContent = '';

  // Render vault
  renderVaultManager();

  // Update badge
  const allFiles = getAllVaultFiles();
  if (allFiles.length > 0) {
    menuEl.jsonBadge.textContent = String(allFiles.length);
  } else {
    menuEl.jsonBadge.textContent = '';
  }
}

function closeJsonFilesPopup() {
  jsonPopup.style.display = 'none';
}

// ─── JSON Popup Event Listeners ──────────────────────────────────────────────
menuEl.btnJsonFiles.addEventListener('click', (e) => {
  e.stopPropagation();
  openJsonFilesPopup();
});

btnCloseJsonPopup.addEventListener('click', closeJsonFilesPopup);
btnRefreshJsonFiles.addEventListener('click', () => {
  openJsonFilesPopup();
});

jsonPopup.addEventListener('click', (e) => {
  if (e.target === jsonPopup) closeJsonFilesPopup();
});

// Keyboard shortcut: Escape closes animation preview, json popup, or dropdown
 document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (animPreviewEl.popup.style.display !== 'none') {
      stopAnimationPreview();
    } else if (jsonPopup.style.display !== 'none') {
      closeJsonFilesPopup();
    } else {
      closeDropdown();
    }
  }
});

// ─── Auto-sync project state on editor changes ──────────────────────────────
const origUpdateJSONPreview = updateJSONPreview;
updateJSONPreview = function() {
  origUpdateJSONPreview();
  if (currentProject) {
    saveCurrentProjectToStorage();
  }
};

// ─── Splash Screen ───────────────────────────────────────────────────────────
const splashEl = $('splashScreen');
const splashRecentList = $('splashRecentList');

function renderSplashRecent() {
  const recent = getRecentProjects();
  if (recent.length === 0) {
    splashRecentList.innerHTML = '<div class="splash-recent-empty">No recent projects.</div>';
    return;
  }
  splashRecentList.innerHTML = recent.map((item, i) => {
    const date = new Date(item.lastOpened);
    const dateStr = date.toLocaleDateString('en-US', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
    return `
      <div class="splash-recent-item" data-index="${i}">
        <div class="splash-recent-info">
          <span class="splash-recent-name">${escapeHtml(item.name)}</span>
          <span class="splash-recent-meta">${escapeHtml(item.path || '(in memory)')} — ${dateStr}</span>
        </div>
        <span class="splash-recent-arrow">→</span>
      </div>
    `;
  }).join('');

  splashRecentList.querySelectorAll('.splash-recent-item').forEach(el => {
    el.addEventListener('click', async () => {
      const i = parseInt(el.dataset.index);
      const recent = getRecentProjects();
      const item = recent[i];
      if (!item || !item.data) return;

      // Try to open the actual .json file from disk
      const texturename = item.data?.editorState?.jsonData?.texturename;
      if (texturename && projectDirHandle) {
        try {
          const texturesDir = await getTexturesDirHandle();
          if (texturesDir) {
            const filename = texturename.replace(/[\/\\]/g, '_') + '.json';
            try {
              const fileHandle = await texturesDir.getFileHandle(filename);
              const file = await fileHandle.getFile();
              const text = await file.text();
              const jsonData = JSON.parse(text);
              loadFromJSON(jsonData);
              hideSplashScreen();
              return;
            } catch { /* fall through */ }
          }
        } catch { /* fall through */ }
      }

      loadProjectData(item.data, item.path);
      hideSplashScreen();
    });
  });
}

function showSplashScreen() {
  renderSplashRecent();
  splashEl.style.display = 'flex';
}

function hideSplashScreen() {
  splashEl.style.display = 'none';
  // Close required-mode dropdown if still showing
  if (projectSetupRequired) {
    projectSetupRequired = false;
    closeDropdown();
  }
}

// ─── Start a new empty project ───────────────────────────────────────────────
function startNewProject() {
  clearCurrentProject();
  animations = [];
  animationIdCounter = 0;
  spritesheetImage = null;
  spritesheetFilename = '';
  spriteZoom = 1;
  stopAnimationPreview();

  // Clear all form fields
  el.texturename.value = '';
  el.propGeneration.value = '';
  el.textureOriginalChance.value = '';
  el.front.checked = false;
  el.lightR.value = '';
  el.lightG.value = '';
  el.lightB.value = '';
  el.lightA.value = '';
  el.lightRange.value = '';
  el.lightIntensity.value = '';
  el.dimWidth.value = '';
  el.dimHeight.value = '';
  el.trailFreq.value = '';

  updateColorPreview();
  renderAnimations();
  updateJSONPreview();
  hideSplashScreen();
}

// ─── Splash screen button wiring ─────────────────────────────────────────────
$('btnSplashNew').addEventListener('click', startNewProject);
$('btnSplashOpen').addEventListener('click', () => {
  openFile();
});
$('btnSplashSetDir').addEventListener('click', () => {
  setupProjectDirectory();
  renderSplashRecent();
});

// ═══════════════════════════════════════════════════════════════════════════════
// DRAG & DROP SUPPORT
// ═══════════════════════════════════════════════════════════════════════════════

const dropOverlay = $('dropOverlay');
const dropInner = dropOverlay?.querySelector('.drop-overlay-inner');
let dropOverlayTimeoutId = null;

function showDropOverlay(highlight = false) {
  if (dropOverlayTimeoutId) {
    clearTimeout(dropOverlayTimeoutId);
    dropOverlayTimeoutId = null;
  }
  dropOverlay.classList.remove('drop-overlay-out');
  dropOverlay.style.display = 'flex';
  if (dropInner) {
    dropInner.classList.toggle('drop-overlay-highlight', highlight);
  }
}

function hideDropOverlay() {
  if (dropOverlayTimeoutId) {
    clearTimeout(dropOverlayTimeoutId);
    dropOverlayTimeoutId = null;
  }
  // Animate out, then hide
  dropOverlay.classList.add('drop-overlay-out');
  dropOverlayTimeoutId = setTimeout(() => {
    dropOverlay.style.display = 'none';
    dropOverlay.classList.remove('drop-overlay-out');
    dropOverlayTimeoutId = null;
  }, 120);
}

function handleDropFile(file) {
  // Validate file type
  const isJSON = file.name.endsWith('.json');
  const isProject = file.name.endsWith('.duq-project');

  if (!isJSON && !isProject) {
    showNotification('Unsupported format. Drop .json or .duq-project files.', 'error');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);

      if (isProject) {
        // .duq-project file — load project data
        loadProjectData(data, file.name);
        hideSplashScreen();
      } else if (data.editorState && data.version) {
        // Could be a .duq-project without the extension — treat as project
        loadProjectData(data, file.name);
        hideSplashScreen();
      } else {
        // Regular .json texture file
        loadFromJSON(data);
      }
    } catch (err) {
      showNotification('Error reading file: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
}

// ─── Drag & Drop Event Listeners ─────────────────────────────────────

document.addEventListener('dragenter', (e) => {
  e.preventDefault();

  // Ignore drag events from animation preview header
  if (e.target.closest('.anim-preview-header')) return;

  // Check if files are being dragged (not text/html selections)
  if (e.dataTransfer.types.includes('Files')) {
    showDropOverlay(false);
  }
});

document.addEventListener('dragover', (e) => {
  e.preventDefault();

  // Update highlight state based on whether valid files are being dragged
  if (e.dataTransfer.types.includes('Files')) {
    const hasValidFile = Array.from(e.dataTransfer.items).some(
      item => item.kind === 'file'
    );
    showDropOverlay(hasValidFile);
  }
});

document.addEventListener('dragleave', (e) => {
  e.preventDefault();

  // Hide only when truly leaving the browser window (cursor outside viewport)
  // This is more reliable than checking relatedTarget which varies across browsers
  if (e.clientX <= 0 || e.clientY <= 0 ||
      e.clientX >= window.innerWidth - 1 || e.clientY >= window.innerHeight - 1) {
    hideDropOverlay();
  }
});

document.addEventListener('drop', (e) => {
  e.preventDefault();
  hideDropOverlay();

  const files = e.dataTransfer.files;
  if (files.length === 0) return;

  const file = files[0];
  handleDropFile(file);
});

// ═══════════════════════════════════════════════════════════════════════════════
// NOTIFICATION TOAST SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

const NOTIFICATION_DURATION = 5000; // ms

function showNotification(message, type = 'error') {
  const container = $('notificationContainer');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `notification notification-${type}`;

  const iconSvg = type === 'error'
    ? '<svg class="notification-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="10" r="9"/><path d="M10 6v5M10 14v.01"/></svg>'
    : '<svg class="notification-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="10" r="9"/><path d="M6 10l3 3 5-5"/></svg>';

  el.innerHTML = `
    ${iconSvg}
    <span class="notification-message"></span>
    <button class="notification-close" title="Close">✕</button>
  `;

  const msgEl = el.querySelector('.notification-message');
  if (msgEl) msgEl.textContent = message;

  const closeBtn = el.querySelector('.notification-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => dismissNotification(el));
  }

  container.appendChild(el);

  // Auto-dismiss after duration
  const timeoutId = setTimeout(() => dismissNotification(el), NOTIFICATION_DURATION);
  el._timeoutId = timeoutId;
}

function dismissNotification(el) {
  if (el._dismissing) return;
  el._dismissing = true;

  if (el._timeoutId) {
    clearTimeout(el._timeoutId);
  }

  el.classList.add('notification-out');
  el.addEventListener('animationend', () => {
    if (el.parentNode) {
      el.parentNode.removeChild(el);
    }
  });
}

// ─── Initialize ──────────────────────────────────────────────────────────────
renderRecentProjects();

// Load the user-provided full path from localStorage
projectFullPath = (() => {
  try {
    let path = localStorage.getItem(STORAGE_KEY_PROJECT_PATH) || '';
    // Normalize backslashes to forward slashes on load
    return path.replace(/\\/g, '/');
  } catch {
    return '';
  }
})();

// Populate the project path input field (if it exists)
const pathInput = $('menuProjectPath');
if (pathInput) {
  pathInput.value = projectFullPath;
}

// Restore the directory handle from IndexedDB (survives page reload)
(async function restoreProjectDirHandle() {
  try {
    const handle = await loadDirHandleFromIDB();
    if (handle) {
      projectDirHandle = handle;
      updateDirDisplay();
    }
  } catch (err) {
    console.warn('Could not restore project directory:', err);
  }
})();

// Always start with the splash screen — never auto-restore a previous session
// Clear any stale current project data to avoid errors on startup
localStorage.removeItem(STORAGE_KEY_CURRENT);
projectSetupRequired = true;
showSplashScreen();
