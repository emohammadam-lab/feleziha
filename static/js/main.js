/**
 * FelezOnline - Core Frontend Scripts
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

  // Load saved theme or default to light
  const savedTheme = localStorage.getItem('felez_theme') || 'light';
  applyTheme(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

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

  // Metal Densities (g/cm³) and estimated reference prices (Toman/kg)
  const metalProps = {
    copper: { density: 8.96, price: 642000, name: 'مس' },
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

  // 4. FAST INLINE PRICE UPDATE (For Sales & Admin Portal)
  const fastPriceForms = document.querySelectorAll('.fast-price-form');
  fastPriceForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const btn = this.querySelector('button[type="submit"]');
      const originalText = btn.innerText;
      btn.innerText = '...';
      btn.disabled = true;

      fetch('/management/fast-price-update/', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        btn.innerText = originalText;
        btn.disabled = false;
        if (data.status === 'success') {
          const prodId = formData.get('product_id');
          const statusContainer = document.getElementById(`price-status-${prodId}`);
          
          if (statusContainer) {
            if (data.mode === 'call') {
              statusContainer.innerHTML = `
                <span class="badge-change neutral" style="background:var(--warning-bg); color:var(--warning-color); font-weight:800;">
                  📞 تماس بگیرید
                </span>
              `;
            } else if (data.mode === 'api') {
              statusContainer.innerHTML = `
                <div style="display:flex; flex-direction:column;">
                  <strong style="color:var(--copper-primary); font-size:0.95rem;">${data.new_price} تومان</strong>
                  <span style="font-size:0.7rem; color:var(--success-color);">✓ متصل به وب‌سرویس</span>
                </div>
              `;
            } else {
              statusContainer.innerHTML = `
                <div style="display:flex; flex-direction:column;">
                  <strong style="color:var(--text-main); font-size:0.95rem;">${data.new_price} تومان</strong>
                  <span style="font-size:0.7rem; color:var(--text-muted);">نرخ دستی کارشناس</span>
                </div>
              `;
            }
          }

          // Inline subtle notification
          const notif = document.createElement('span');
          notif.innerText = '✓ ذخیره شد';
          notif.style.color = '#16a34a';
          notif.style.fontSize = '0.75rem';
          notif.style.fontWeight = '700';
          notif.style.marginRight = '0.4rem';
          btn.parentNode.appendChild(notif);
          setTimeout(() => { notif.remove(); }, 2500);

        } else {
          alert('خطا: ' + (data.message || 'خطایی رخ داد'));
        }
      })
      .catch(err => {
        btn.innerText = originalText;
        btn.disabled = false;
        alert('خطای اتصال به سرور');
      });
    });
  });
});
