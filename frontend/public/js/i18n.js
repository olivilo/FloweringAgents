/**
 * Flower i18n — lightweight client-side translations
 * Usage:
 *   <span data-i18n="nav.stories"></span>
 *   <input data-i18n-placeholder="search.placeholder">
 *
 *   window.i18n.setLang('de')
 */

class FlowerI18n {
  constructor() {
    this.lang = localStorage.getItem('flower_lang')
      || (navigator.language || 'en').slice(0, 2)
      || 'en';
    if (!['de', 'en'].includes(this.lang)) this.lang = 'en';
    this.cache = {};
  }

  async init() {
    await this._load(this.lang);
    this._apply();
    document.documentElement.lang = this.lang;
  }

  async setLang(lang) {
    if (!['de', 'en'].includes(lang)) return;
    this.lang = lang;
    localStorage.setItem('flower_lang', lang);
    await this._load(lang);
    this._apply();
    document.documentElement.lang = lang;
    // Update switcher buttons
    document.querySelectorAll('[data-lang-btn]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.langBtn === lang);
    });
    // Fire custom event so story pages can re-render content
    window.dispatchEvent(new CustomEvent('flower:langchange', { detail: { lang } }));
  }

  t(key, vars = {}) {
    const strings = this.cache[this.lang] || {};
    let str = key.split('.').reduce((o, k) => o?.[k], strings) ?? key;
    Object.entries(vars).forEach(([k, v]) => {
      str = str.replace(`{${k}}`, v);
    });
    return str;
  }

  async _load(lang) {
    if (this.cache[lang]) return;
    try {
      const r = await fetch(`/i18n/${lang}.json`);
      this.cache[lang] = await r.json();
    } catch {
      this.cache[lang] = {};
    }
  }

  _apply() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const val = this.t(el.dataset.i18n);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.value = val;
      } else {
        el.textContent = val;
      }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = this.t(el.dataset.i18nPlaceholder);
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      el.title = this.t(el.dataset.i18nTitle);
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      el.innerHTML = this.t(el.dataset.i18nHtml);
    });
  }
}

window.i18n = new FlowerI18n();
document.addEventListener('DOMContentLoaded', () => window.i18n.init());
