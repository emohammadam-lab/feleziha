/**
 * Feleziha (فلزی‌ها) - Core Frontend Scripts
 * - Day / Night Theme Toggle with LocalStorage
 * - Real-time Metal Weight & Price Calculator
 * - Metal Tabs Switcher
 * - Admin / Sales Quick Price Update AJAX
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. DAY / NIGHT THEME SWITCHER
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const themeIcon = document.getElementById('theme-icon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('felez_theme', theme);
    if (themeIcon) {
      if (theme === 'dark') {
        // Moon icon / Sun switch
        themeIcon.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>`;
      } else {
        themeIcon.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>`;
      }
    }
  }

  // Load saved theme or default to dark gray
  const savedTheme = localStorage.getItem('felez_theme') || 'dark';
  applyTheme(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

  // 1.1 FADE & FLAT DROPDOWN TOGGLE (Mobile, Tablet & Desktop Touch)
  const navDropdowns = document.querySelectorAll('.nav-dropdown');

  navDropdowns.forEach(dropdown => {
    const trigger = dropdown.querySelector('.nav-dropdown-trigger');
    if (trigger) {
      trigger.addEventListener('click', function (e) {
        if (window.innerWidth <= 992 || ('ontouchstart' in window)) {
          e.preventDefault();
          const isActive = dropdown.classList.contains('is-active');
          navDropdowns.forEach(d => d.classList.remove('is-active'));
          if (!isActive) {
            dropdown.classList.add('is-active');
          }
        }
      });
    }
  });

  // Close dropdown on click outside
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-dropdown')) {
      navDropdowns.forEach(d => d.classList.remove('is-active'));
    }
  });

  // 2. METAL CATEGORY TABS SWITCHER (Homepage)
  const tabButtons = document.querySelectorAll('.metal-tab-btn');
  const tabPanes = document.querySelectorAll('.metal-tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');

      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.style.display = 'none');

      this.classList.add('active');
      const activePane = document.getElementById(targetId);
      if (activePane) {
        activePane.style.display = 'block';
      }
    });
  });

  // 3. INTERACTIVE METAL WEIGHT & PRICE CALCULATOR
  const calcMetal = document.getElementById('calc-metal');
  const calcShape = document.getElementById('calc-shape');
  const calcL = document.getElementById('calc-length');
  const calcW = document.getElementById('calc-width');
  const calcT = document.getElementById('calc-thickness');
  const calcD = document.getElementById('calc-diameter');
  const calcQty = document.getElementById('calc-quantity');

  const weightDisplay = document.getElementById('calc-result-weight');
  const priceDisplay = document.getElementById('calc-result-price');

  // Metal Densities (g/cm³) and estimated reference prices (Toman/kg - پایه نرخ مس ۳,۴۲۰,۰۰۰ تومان)
  const metalProps = {
    copper: { density: 8.96, price: 3420000, name: 'مس' },
    aluminum: { density: 2.70, price: 238000, name: 'آلومینیوم' },
    steel: { density: 7.85, price: 32400, name: 'فولاد و آهن' },
    brass: { density: 8.50, price: 520000, name: 'برنج' },
    zinc: { density: 7.14, price: 268000, name: 'روی' }
  };

  function updateCalculatorShapeFields() {
    if (!calcShape) return;
    const shape = calcShape.value;
    const groupW = document.getElementById('group-width');
    const groupD = document.getElementById('group-diameter');
    const groupT = document.getElementById('group-thickness');

    if (shape === 'sheet') {
      if (groupW) groupW.style.display = 'block';
      if (groupT) groupT.style.display = 'block';
      if (groupD) groupD.style.display = 'none';
    } else if (shape === 'tube') {
      if (groupW) groupW.style.display = 'none';
      if (groupD) groupD.style.display = 'block';
      if (groupT) groupT.style.display = 'block';
    } else if (shape === 'rod') {
      if (groupW) groupW.style.display = 'none';
      if (groupD) groupD.style.display = 'block';
      if (groupT) groupT.style.display = 'none';
    } else if (shape === 'strip') {
      if (groupW) groupW.style.display = 'block';
      if (groupT) groupT.style.display = 'block';
      if (groupD) groupD.style.display = 'none';
    }
    calculateMetalWeight();
  }

  function calculateMetalWeight() {
    if (!calcMetal || !weightDisplay) return;

    const metalKey = calcMetal.value;
    const shape = calcShape.value;
    const metal = metalProps[metalKey] || metalProps.copper;
    const density = metal.density; // g/cm³

    const length = parseFloat(calcL ? calcL.value : 1000) || 1000; // mm
    const width = parseFloat(calcW ? calcW.value : 1000) || 1000;  // mm
    const thickness = parseFloat(calcT ? calcT.value : 2) || 2;    // mm
    const diameter = parseFloat(calcD ? calcD.value : 20) || 20;   // mm
    const qty = parseInt(calcQty ? calcQty.value : 1, 10) || 1;

    let volumeCm3 = 0; // cm³

    if (shape === 'sheet' || shape === 'strip') {
      // Volume = (L mm / 10) * (W mm / 10) * (T mm / 10)
      volumeCm3 = (length / 10) * (width / 10) * (thickness / 10);
    } else if (shape === 'rod') {
      // Cylindrical rod: pi * r^2 * L
      const radiusCm = (diameter / 2) / 10;
      const lengthCm = length / 10;
      volumeCm3 = Math.PI * Math.pow(radiusCm, 2) * lengthCm;
    } else if (shape === 'tube') {
      // Hollow tube: pi * (R_out^2 - R_in^2) * L
      const rOutCm = (diameter / 2) / 10;
      const rInCm = Math.max(0, (diameter / 2 - thickness) / 10);
      const lengthCm = length / 10;
      volumeCm3 = Math.PI * (Math.pow(rOutCm, 2) - Math.pow(rInCm, 2)) * lengthCm;
    }

    const singleWeightKg = (volumeCm3 * density) / 1000;
    const totalWeightKg = singleWeightKg * qty;
    const estimatedPrice = totalWeightKg * metal.price;

    weightDisplay.innerText = totalWeightKg.toFixed(2) + ' کیلوگرم';
    if (priceDisplay) {
      priceDisplay.innerText = Math.round(estimatedPrice).toLocaleString('fa-IR') + ' تومان';
    }
  }

  if (calcMetal) {
    calcMetal.addEventListener('change', calculateMetalWeight);
    calcShape.addEventListener('change', updateCalculatorShapeFields);
    [calcL, calcW, calcT, calcD, calcQty].forEach(input => {
      if (input) input.addEventListener('input', calculateMetalWeight);
    });
    updateCalculatorShapeFields();
  }

  // ==========================================
  // 4. CSRF & TOAST NOTIFICATION UTILITIES
  // ==========================================
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  window.showToast = function(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === 'error') {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    }

    toast.innerHTML = `
      ${iconSvg}
      <span style="flex:1;">${message}</span>
      <button type="button" style="background:none; border:none; color:inherit; cursor:pointer; opacity:0.6; font-size:1.1rem; padding:0; line-height:1; margin-right:0.4rem;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(12px)';
      toast.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  };

  // ==========================================
  // 5. AGILE PRICING WORKFLOW (ONE-CLICK)
  // ==========================================
  function updatePriceStatusDisplay(prodId, mode, displayText, rawPrice) {
    const statusContainer = document.getElementById(`price-status-${prodId}`);
    if (statusContainer) {
      if (mode === 'call') {
        statusContainer.innerHTML = `
          <span class="badge-change neutral" style="background:var(--warning-bg); color:var(--warning-color); font-weight:800;">
            📞 تماس بگیرید
          </span>
        `;
      } else if (mode === 'api') {
        statusContainer.innerHTML = `
          <div style="display:flex; flex-direction:column;">
            <strong style="color:var(--copper-primary); font-size:1rem;">${displayText}</strong>
            <span style="font-size:0.7rem; color:var(--success-color); font-weight:700;">✓ وب‌سرویس زنده بورس</span>
          </div>
        `;
      } else {
        statusContainer.innerHTML = `
          <div style="display:flex; flex-direction:column;">
            <strong style="color:var(--text-main); font-size:1rem;">${displayText}</strong>
            <span style="font-size:0.7rem; color:#2563eb; font-weight:600;">نرخ دستی کارشناس</span>
          </div>
        `;
      }
    }

    // Update row attribute for instant filtering
    const row = document.getElementById(`row-prod-${prodId}`);
    if (row) {
      row.setAttribute('data-mode', mode);
    }

    // Update manual box accessibility
    const manualBox = document.getElementById(`manual-box-${prodId}`);
    const inputPrice = document.getElementById(`input-price-${prodId}`);
    if (manualBox && inputPrice) {
      if (mode === 'manual') {
        manualBox.style.opacity = '1';
        manualBox.style.pointerEvents = 'auto';
        inputPrice.disabled = false;
        if (rawPrice && rawPrice > 0) {
          inputPrice.value = rawPrice;
        }
      } else {
        manualBox.style.opacity = '0.35';
        manualBox.style.pointerEvents = 'none';
        inputPrice.disabled = true;
      }
    }
  }

  function sendAgilePriceUpdate(prodId, mode, newPrice = null, callback = null) {
    const csrfToken = getCsrfToken();
    const formData = new FormData();
    formData.append('product_id', prodId);
    formData.append('pricing_mode', mode);
    if (newPrice !== null && newPrice !== undefined) {
      formData.append('new_price', newPrice);
    }

    fetch('/management/fast-price-update/', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        updatePriceStatusDisplay(prodId, data.mode, data.new_price ? `${data.new_price} تومان` : data.display_text, data.raw_price);
        showToast(data.message, 'success');
        if (callback) callback(null, data);
      } else {
        showToast('خطا: ' + (data.message || 'عملیات ناموفق بود'), 'error');
        if (callback) callback(data.message);
      }
    })
    .catch(err => {
      showToast('خطای ارتباط با سرور. لطفاً مجدداً تلاش فرمایید.', 'error');
      if (callback) callback(err);
    });
  }

  // Segmented Mode Switcher (One-Click)
  const modeSwitchBtns = document.querySelectorAll('.btn-mode-switch');
  modeSwitchBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const prodId = this.getAttribute('data-prod-id');
      const targetMode = this.getAttribute('data-mode');
      const parentControl = this.closest('.pricing-segmented-control');

      if (!parentControl) return;

      // Optimistic UI toggle
      parentControl.querySelectorAll('.btn-mode-switch').forEach(b => {
        b.classList.remove('active-manual', 'active-api', 'active-call');
      });
      this.classList.add(`active-${targetMode}`);

      // Manual input focus if manual
      const inputPrice = document.getElementById(`input-price-${prodId}`);
      let currentPriceVal = null;
      if (targetMode === 'manual' && inputPrice && inputPrice.value) {
        currentPriceVal = inputPrice.value;
      }

      sendAgilePriceUpdate(prodId, targetMode, currentPriceVal, (err) => {
        if (!err && targetMode === 'manual' && inputPrice) {
          inputPrice.focus();
        }
      });
    });
  });

  // Save Manual Price (Submit Button)
  const saveManualBtns = document.querySelectorAll('.btn-save-manual');
  saveManualBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const prodId = this.getAttribute('data-prod-id');
      const input = document.getElementById(`input-price-${prodId}`);
      if (!input || !input.value.trim()) {
        showToast('لطفاً نرخ جدید را به تومان وارد فرمایید.', 'warning');
        if (input) input.focus();
        return;
      }
      const originalText = this.innerText;
      this.innerText = '...';
      this.disabled = true;

      sendAgilePriceUpdate(prodId, 'manual', input.value.trim(), () => {
        this.innerText = originalText;
        this.disabled = false;
      });
    });
  });

  // Enter key on agile price input
  const agileInputs = document.querySelectorAll('.agile-price-input');
  agileInputs.forEach(input => {
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const prodId = this.getAttribute('data-prod-id');
        if (!this.value.trim()) {
          showToast('لطفاً نرخ جدید را وارد فرمایید.', 'warning');
          return;
        }
        sendAgilePriceUpdate(prodId, 'manual', this.value.trim());
      }
    });
  });

  // Quick Step Buttons (+5k / -5k)
  const quickStepBtns = document.querySelectorAll('.btn-quick-step');
  quickStepBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const prodId = this.getAttribute('data-prod-id');
      const step = parseInt(this.getAttribute('data-step'), 10) || 0;
      const input = document.getElementById(`input-price-${prodId}`);
      if (!input) return;

      let currentVal = parseInt(input.value.replace(/[^0-9]/g, ''), 10) || 0;
      let nextVal = Math.max(0, currentVal + step);
      input.value = nextVal;

      // Make segmented button active-manual if not already
      const parentRow = document.getElementById(`row-prod-${prodId}`);
      if (parentRow) {
        const segControl = parentRow.querySelector('.pricing-segmented-control');
        if (segControl) {
          segControl.querySelectorAll('.btn-mode-switch').forEach(b => {
            b.classList.remove('active-manual', 'active-api', 'active-call');
            if (b.getAttribute('data-mode') === 'manual') {
              b.classList.add('active-manual');
            }
          });
        }
      }

      sendAgilePriceUpdate(prodId, 'manual', nextVal);
    });
  });

  // Client-Side Search and Mode Filtering
  const searchInput = document.getElementById('admin-product-search');
  const filterChips = document.querySelectorAll('.pricing-filter-chip');
  let currentFilterMode = 'all';

  function filterPricingTable() {
    const searchTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const rows = document.querySelectorAll('.pricing-row');

    rows.forEach(row => {
      const rowTitle = (row.getAttribute('data-title') || '').toLowerCase();
      const rowMode = row.getAttribute('data-mode') || 'manual';

      const matchesSearch = !searchTerm || rowTitle.includes(searchTerm);
      const matchesFilter = currentFilterMode === 'all' || rowMode === currentFilterMode;

      if (matchesSearch && matchesFilter) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterPricingTable);
  }

  filterChips.forEach(chip => {
    chip.addEventListener('click', function () {
      filterChips.forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      currentFilterMode = this.getAttribute('data-filter') || 'all';
      filterPricingTable();
    });
  });

  // 6. LEGACY FAST INLINE PRICE UPDATE (For any inline forms)
  const fastPriceForms = document.querySelectorAll('.fast-price-form');
  fastPriceForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const btn = this.querySelector('button[type="submit"]');
      const originalText = btn ? btn.innerText : 'ثبت';
      if (btn) {
        btn.innerText = '...';
        btn.disabled = true;
      }

      fetch('/management/fast-price-update/', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCsrfToken()
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (btn) {
          btn.innerText = originalText;
          btn.disabled = false;
        }
        if (data.status === 'success') {
          showToast(data.message, 'success');
        } else {
          showToast('خطا: ' + (data.message || 'خطایی رخ داد'), 'error');
        }
      })
      .catch(err => {
        if (btn) {
          btn.innerText = originalText;
          btn.disabled = false;
        }
        showToast('خطای اتصال به سرور', 'error');
      });
    });
  });
});
