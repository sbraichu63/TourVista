/* ================================================================
   TourVista India — Main JavaScript
   ================================================================ */

'use strict';

// ── NAVBAR SCROLL BEHAVIOUR ──────────────────────────────────────
(function () {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  const isTransparent = navbar.classList.contains('transparent');

  window.addEventListener('scroll', () => {
    if (isTransparent) {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
    }
  }, { passive: true });
})();

// ── HAMBURGER / MOBILE MENU ──────────────────────────────────────
(function () {
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    const isOpen = mobileMenu.classList.contains('open');
    hamburger.querySelectorAll('span').forEach((s, i) => {
      if (isOpen) {
        if (i === 0) s.style.transform = 'rotate(45deg) translate(5px, 5px)';
        if (i === 1) s.style.opacity = '0';
        if (i === 2) s.style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        s.style.transform = '';
        s.style.opacity = '';
      }
    });
  });

  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
})();

// ── TOAST MESSAGES ───────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4500) {
  const container = document.querySelector('.toast-container') || createToastContainer();

  const icons = { success: 'fa-check-circle', danger: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i class="fas ${icons[type] || icons.info} toast-icon"></i>
    <div class="toast-msg">${message}</div>
    <i class="fas fa-times toast-close" onclick="this.closest('.toast').remove()"></i>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.className = 'toast-container';
  document.body.appendChild(div);
  return div;
}

// Auto-dismiss Django messages
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.django-message').forEach(el => {
    showToast(el.dataset.message, el.dataset.type || 'info');
  });
});

// ── SCROLL TO TOP ────────────────────────────────────────────────
(function () {
  const btn = document.createElement('button');
  btn.className = 'scroll-top';
  btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
  btn.setAttribute('aria-label', 'Scroll to top');
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
})();

// ── AOS (Animate On Scroll) ──────────────────────────────────────
(function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.aosDelay || 0;
        setTimeout(() => {
          entry.target.classList.add('aos-animate');
        }, Number(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('[data-aos]').forEach(el => observer.observe(el));
})();

// ── PACKAGE DETAIL — TABS ────────────────────────────────────────
(function () {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');
  if (!tabBtns.length) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = document.getElementById(btn.dataset.tab);
      if (panel) panel.classList.add('active');
    });
  });
})();

// ── GALLERY THUMBNAILS ───────────────────────────────────────────
(function () {
  const mainImg = document.getElementById('main-gallery-img');
  const thumbs = document.querySelectorAll('.gallery-thumb');
  if (!mainImg || !thumbs.length) return;

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      mainImg.src = thumb.dataset.src;
      mainImg.style.animation = 'none';
      mainImg.offsetHeight; // reflow
      mainImg.style.animation = 'fadeIn .4s ease';
    });
  });
})();

// ── STAR RATING ──────────────────────────────────────────────────
(function () {
  const labels = document.querySelectorAll('.star-rating label');
  labels.forEach(label => {
    label.addEventListener('mouseenter', function () {
      const thisIdx = [...labels].indexOf(this);
      labels.forEach((l, i) => {
        l.style.color = i <= thisIdx ? '#F59E0B' : '';
      });
    });
    label.addEventListener('mouseleave', () => {
      labels.forEach(l => l.style.color = '');
    });
  });
})();

// ── WISHLIST TOGGLE ──────────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-wishlist]');
  if (!btn) return;

  const pkgId = btn.dataset.wishlist;
  const icon = btn.querySelector('i') || btn;

  try {
    const resp = await fetch(`/wishlist/toggle/${pkgId}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });
    const data = await resp.json();

    if (data.status === 'added') {
      btn.classList.add('active');
      showToast('❤️ Added to your wishlist!', 'success', 2500);
    } else {
      btn.classList.remove('active');
      showToast('💔 Removed from wishlist.', 'info', 2500);
    }
  } catch {
    showToast('Please log in to use wishlist.', 'warning');
  }
});

// ── PAYMENT METHOD SELECTOR ──────────────────────────────────────
(function () {
  const methodCards = document.querySelectorAll('.payment-method-card');
  if (!methodCards.length) return;

  methodCards.forEach(card => {
    card.addEventListener('click', () => {
      methodCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      card.querySelector('input[type="radio"]').checked = true;

      // Show correct fields
      document.querySelectorAll('.payment-fields').forEach(f => f.classList.remove('active'));
      const method = card.querySelector('input').value;
      const fields = document.getElementById(`fields-${method}`);
      if (fields) fields.classList.add('active');
    });
  });

  // Select first by default
  if (methodCards[0]) methodCards[0].click();
})();

// ── CARD NUMBER FORMATTING ───────────────────────────────────────
(function () {
  const cardInput = document.getElementById('id_card_number');
  if (!cardInput) return;
  cardInput.addEventListener('input', function () {
    let val = this.value.replace(/\D/g, '').slice(0, 16);
    this.value = val.replace(/(.{4})/g, '$1 ').trim();
  });
  const expiryInput = document.getElementById('id_card_expiry');
  if (expiryInput) {
    expiryInput.addEventListener('input', function () {
      let val = this.value.replace(/\D/g, '').slice(0, 4);
      if (val.length >= 3) val = val.slice(0, 2) + '/' + val.slice(2);
      this.value = val;
    });
  }
})();

// ── PASSWORD STRENGTH ────────────────────────────────────────────
(function () {
  const pwInput = document.getElementById('id_password1');
  const strengthBar = document.getElementById('strength-fill');
  const strengthLabel = document.getElementById('strength-label');
  if (!pwInput || !strengthBar) return;

  const strengthColors = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981'];
  const strengthLabels = ['Too Weak', 'Fair', 'Good', 'Strong!'];

  pwInput.addEventListener('input', function () {
    const val = this.value;
    let score = 0;
    if (val.length >= 8) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const pct = (score / 4) * 100;
    strengthBar.style.width = pct + '%';
    strengthBar.style.background = strengthColors[score - 1] || '#E5E7EB';
    strengthLabel.textContent = score > 0 ? strengthLabels[score - 1] : 'Enter password';
    strengthLabel.style.color = strengthColors[score - 1] || '#9CA3AF';
  });
})();

// ── LIVE FORM VALIDATION ─────────────────────────────────────────
(function () {
  function validate(input) {
    const val = input.value.trim();
    let error = '';

    if (input.required && !val) {
      error = 'This field is required.';
    } else if (input.type === 'email' && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
      error = 'Please enter a valid email.';
    } else if (input.type === 'tel' && val && !/^[\+]?[0-9]{10,13}$/.test(val.replace(/\s/g, ''))) {
      error = 'Please enter a valid phone number.';
    } else if (input.minLength > 0 && val && val.length < input.minLength) {
      error = `Minimum ${input.minLength} characters required.`;
    }

    const errEl = input.closest('.form-group')?.querySelector('.form-error');
    if (errEl) {
      errEl.textContent = error;
      errEl.style.display = error ? 'flex' : 'none';
    }
    input.classList.toggle('is-invalid', !!error);
    input.classList.toggle('is-valid', !error && !!val);
    return !error;
  }

  document.querySelectorAll('.form-control').forEach(input => {
    input.addEventListener('blur', () => validate(input));
    input.addEventListener('input', () => {
      if (input.classList.contains('is-invalid')) validate(input);
    });
  });
})();

// ── AI CHATBOT ───────────────────────────────────────────────────
(function () {
  class ChatBot {
    constructor() {
      this.toggle = document.getElementById('chatbot-toggle');
      this.window = document.getElementById('chatbot-window');
      this.closeBtn = document.getElementById('chatbot-close');
      this.clearBtn = document.getElementById('chatbot-clear');
      this.messagesContainer = document.getElementById('chatbot-messages');
      this.quickRepliesContainer = document.getElementById('chatbot-quick-replies');
      this.input = document.getElementById('chatbot-input');
      this.sendBtn = document.getElementById('chatbot-send');
      
      this.isOpen = false;
      this.history = JSON.parse(sessionStorage.getItem('tourvista_chat_history')) || [];
      
      if (!this.toggle || !this.window) return;
      this.init();
    }

    init() {
      this.toggle.addEventListener('click', () => this.toggleChat());
      this.closeBtn?.addEventListener('click', () => this.toggleChat(false));
      this.clearBtn?.addEventListener('click', () => this.clearChat());
      
      this.sendBtn?.addEventListener('click', () => this.handleUserInput());
      this.input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.handleUserInput();
        }
      });

      // Load history
      if (this.history.length > 0) {
        this.renderHistory();
      } else {
        this.addBotMsg("🙏 Namaste! I'm Vistara, your TourVista travel assistant!\n\nI can help you find the perfect tour, plan your budget, or give travel tips for India. 🌏", false);
        this.showQuickReplies(['🌅 Rajasthan', '🏖️ Goa', '🏔️ Manali', '❄️ Kashmir', '💰 Budget Tips']);
      }
    }

    toggleChat(force) {
      this.isOpen = force !== undefined ? force : !this.isOpen;
      this.window.classList.toggle('open', this.isOpen);
      this.toggle.innerHTML = this.isOpen ? '<i class="fas fa-times"></i>' : '<i class="fas fa-comments"></i>';
      this.toggle.setAttribute('aria-expanded', this.isOpen);
      
      if (this.isOpen) {
        setTimeout(() => this.input?.focus(), 400);
        this.scrollToBottom();
      }
    }

    clearChat() {
      this.history = [];
      sessionStorage.removeItem('tourvista_chat_history');
      this.messagesContainer.innerHTML = '';
      this.addBotMsg("Chat cleared! How can I help you today? 🙏", false);
      this.showQuickReplies(['🌅 Rajasthan', '🏖️ Goa', '🏔️ Manali', '❄️ Kashmir', '💰 Budget Tips']);
    }

    addMsg(text, sender = 'bot', save = true, richData = null) {
      const msgObj = { text, sender, richData, timestamp: new Date().getTime() };
      if (save) {
        this.history.push(msgObj);
        sessionStorage.setItem('tourvista_chat_history', JSON.stringify(this.history));
      }

      const div = document.createElement('div');
      div.className = `chat-msg ${sender}`;
      
      const avatar = sender === 'bot' ? '🌏' : '<i class="fas fa-user" style="font-size:.75rem"></i>';
      
      let richHtml = '';
      if (richData && richData.tours) {
        richHtml = `<div class="chat-tours">
          ${richData.tours.map(t => `
            <div class="chat-tour-card">
              <img src="${t.image || '/static/img/placeholder.jpg'}" class="chat-tour-img" alt="${t.title}">
              <div class="chat-tour-info">
                <h5>${t.title}</h5>
                <div class="chat-tour-price">₹${t.price}</div>
              </div>
              <a href="${t.url}" class="chat-tour-link">View Package</a>
            </div>
          `).join('')}
        </div>`;
      }

      div.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div class="msg-bubble">
          <div class="msg-text">${this.parseMarkdown(text)}</div>
          ${richHtml}
        </div>
      `;
      
      this.messagesContainer.appendChild(div);
      this.scrollToBottom();
      return div;
    }

    addBotMsg(text, save = true, richData = null) {
      return this.addMsg(text, 'bot', save, richData);
    }

    addUserMsg(text, save = true) {
      return this.addMsg(text, 'user', save);
    }

    showTyping() {
      const div = document.createElement('div');
      div.className = 'chat-msg bot typing-indicator-msg';
      div.innerHTML = `
        <div class="msg-avatar">🌏</div>
        <div class="chat-typing"><span></span><span></span><span></span></div>
      `;
      this.messagesContainer.appendChild(div);
      this.scrollToBottom();
      return div;
    }

    showQuickReplies(replies) {
      this.quickRepliesContainer.innerHTML = '';
      replies.forEach(r => {
        const btn = document.createElement('button');
        btn.className = 'quick-reply';
        btn.textContent = r;
        btn.onclick = () => {
          this.quickRepliesContainer.innerHTML = '';
          this.sendMessage(r);
        };
        this.quickRepliesContainer.appendChild(btn);
      });
      this.scrollToBottom();
    }

    async handleUserInput() {
      const text = this.input.value.trim();
      if (!text) return;
      this.input.value = '';
      await this.sendMessage(text);
    }

    async sendMessage(text) {
      this.addUserMsg(text);
      const typing = this.showTyping();

      try {
        const resp = await fetch('/api/chatbot/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ message: text }),
        });
        const data = await resp.json();
        typing.remove();
        
        const richData = data.tours ? { tours: data.tours } : null;
        this.addBotMsg(data.reply || "I'm sorry, I couldn't understand that. Try asking about a destination!", true, richData);
        
        if (data.quick_replies) {
          this.showQuickReplies(data.quick_replies);
        }
      } catch (e) {
        typing.remove();
        this.addBotMsg('Sorry, I\'m having trouble connecting. Please try again! 🙏');
      }
    }

    parseMarkdown(text) {
      if (!text) return '';
      // Simple regex based markdown parsing
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="chat-link">$1</a>')
        .replace(/\n/g, '<br>');
    }

    renderHistory() {
      this.messagesContainer.innerHTML = '';
      this.history.forEach(m => {
        this.addMsg(m.text, m.sender, false, m.richData);
      });
    }

    scrollToBottom() {
      setTimeout(() => {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
      }, 50);
    }
  }

  // Initialize on load
  document.addEventListener('DOMContentLoaded', () => {
    window.vistarBot = new ChatBot();
  });
})();


// ── WEATHER WIDGET ───────────────────────────────────────────────
async function loadWeather(city) {
  const widget = document.getElementById('weather-widget');
  if (!widget) return;

  try {
    const resp = await fetch(`/api/weather/?city=${encodeURIComponent(city)}`);
    const d = await resp.json();
    if (d.error) return;

    widget.innerHTML = `
      <div class="weather-widget">
        <div class="weather-city"><i class="fas fa-map-marker-alt"></i> ${d.city}</div>
        <div style="display:flex;align-items:flex-end;gap:.5rem">
          <div class="weather-temp">${d.temp}°</div>
          <img src="https://openweathermap.org/img/wn/${d.icon}@2x.png" style="width:50px;height:50px;margin-bottom:.3rem" alt="${d.description}" onerror="this.style.display='none'">
        </div>
        <div class="weather-desc">${d.description}</div>
        <div class="weather-meta">
          <span><i class="fas fa-tint"></i> ${d.humidity}%</span>
          <span><i class="fas fa-wind"></i> ${d.wind_speed} km/h</span>
          <span><i class="fas fa-thermometer-half"></i> Feels ${d.feels_like}°C</span>
        </div>
        ${d.forecast?.length ? `
        <div class="weather-forecast">
          ${d.forecast.map(f => `
            <div class="forecast-day">
              <div class="day">${f.day}</div>
              <img src="https://openweathermap.org/img/wn/${f.icon}.png" style="width:28px;margin:auto" alt="">
              <div class="temps">${f.high}° / ${f.low}°</div>
            </div>`).join('')}
        </div>` : ''}
        ${d.mock ? '<div style="margin-top:.5rem;font-size:.7rem;opacity:.5">* Sample weather data. Add OWM API key for live data.</div>' : ''}
      </div>`;
  } catch (e) {
    console.warn('Weather fetch failed:', e);
  }
}

// ── BUDGET CALCULATOR ─────────────────────────────────────────────
(function () {
  const form = document.getElementById('budget-form');
  if (!form) return;

  const destEl    = document.getElementById('b-dest');
  const daysEl    = document.getElementById('b-days');
  const daysLabel = document.getElementById('b-days-val');
  const travEl    = document.getElementById('b-travellers');
  const travLabel = document.getElementById('b-trav-val');
  const accomEl   = document.getElementById('b-accom');
  const accomBtns = document.querySelectorAll('.b-accom-btn');

  function updateLabels() {
    if (daysLabel && daysEl)     daysLabel.textContent = daysEl.value + ' days';
    if (travLabel && travEl)     travLabel.textContent = travEl.value + ' people';
  }

  [daysEl, travEl].forEach(el => el?.addEventListener('input', () => { updateLabels(); calculate(); }));
  destEl?.addEventListener('change', calculate);

  accomBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      accomBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (accomEl) {
        accomEl.value = btn.dataset.value;
        calculate();
      }
    });
  });

  updateLabels();

  async function calculate() {
    const params = new URLSearchParams({
      destination: destEl?.value || 'default',
      days: daysEl?.value || 5,
      travellers: travEl?.value || 2,
      accommodation: accomEl?.value || 'budget',
    });

    try {
      const resp = await fetch(`/api/budget/?${params}`);
      const d = await resp.json();
      renderResult(d);
    } catch { }
  }

  function renderResult(d) {
    const total = d.grand_total;
    const breakdown = d.breakdown;
    const colors = {
      hotel: '#FF6B35', food: '#F59E0B', transport: '#3B82F6',
      activities: '#10B981', flights: '#8B5CF6'
    };

    const totalEl = document.getElementById('budget-total');
    const perPersonEl = document.getElementById('budget-per-person');
    
    if (totalEl) totalEl.textContent = '₹' + d.grand_total.toLocaleString('en-IN');
    if (perPersonEl) perPersonEl.textContent = '₹' + d.per_person.toLocaleString('en-IN') + ' per person';

    const barsHtml = Object.entries(breakdown).map(([key, val]) => {
      const pct = total > 0 ? (val / total) * 100 : 0;
      const label = key.charAt(0).toUpperCase() + key.slice(1);
      return `
        <div class="budget-bar-item">
          <div class="budget-bar-info">
            <span>${label}</span>
            <span class="budget-bar-amount">₹${val.toLocaleString('en-IN')}</span>
          </div>
          <div class="budget-bar-track">
            <div class="budget-bar-fill" style="width:${pct}%;background:${colors[key] || '#6B7280'}"></div>
          </div>
        </div>`;
    }).join('');

    const barsEl = document.getElementById('budget-bars');
    if (barsEl) barsEl.innerHTML = barsHtml;
  }

  calculate(); // initial
})();


// ── INDIA MAP (LEAFLET) ──────────────────────────────────────────
async function initIndiaMap() {
  const mapEl = document.getElementById('india-map');
  if (!mapEl || typeof L === 'undefined') return;

  const map = L.map('india-map', {
    center: [20.5937, 78.9629],
    zoom: 5,
    zoomControl: true,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);

  try {
    const resp = await fetch('/api/destinations/');
    const { destinations } = await resp.json();

    const customIcon = L.divIcon({
      className: '',
      html: `<div style="width:28px;height:28px;background:linear-gradient(135deg,#FF6B35,#E55520);border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid white;box-shadow:0 3px 10px rgba(0,0,0,.3)"></div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -30],
    });

    destinations.forEach(dest => {
      const marker = L.marker([dest.lat, dest.lng], { icon: customIcon }).addTo(map);
      marker.bindPopup(`
        <div style="font-family:Inter,sans-serif;text-align:center;padding:.5rem">
          <b style="color:#0D1B2A;font-size:1rem">${dest.name}</b><br>
          <span style="color:#6B7280;font-size:.8rem">${dest.state}</span><br>
          <span style="background:#FF6B35;color:white;padding:.15rem .5rem;border-radius:99px;font-size:.72rem;margin-top:.3rem;display:inline-block">${dest.type}</span>
        </div>`, { maxWidth: 180 });
    });
  } catch (e) {
    console.warn('Map destinations load failed:', e);
  }
}

// ── UTILITY ──────────────────────────────────────────────────────
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : '';
}

// ── INIT ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Auto-init map if present
  if (document.getElementById('india-map')) {
    if (typeof L !== 'undefined') {
      initIndiaMap();
    } else {
      // Load Leaflet dynamically
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);

      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = initIndiaMap;
      document.head.appendChild(script);
    }
  }

  // Booking total updater
  const numTrav = document.getElementById('id_num_travellers');
  const pricePerPerson = parseFloat(document.getElementById('price-per-person')?.dataset?.price || 0);
  const totalEl = document.getElementById('booking-total');

  if (numTrav && totalEl && pricePerPerson) {
    numTrav.addEventListener('input', () => {
      const n = parseInt(numTrav.value) || 1;
      const total = pricePerPerson * n;
      totalEl.textContent = '₹' + total.toLocaleString('en-IN');
    });
  }
});
