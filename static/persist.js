/**
 * duq-tools Persistence Utility
 * Shared functions for auto-saving/restoring tool state in localStorage.
 * Included by each tool's HTML.
 */

(function() {
  'use strict';

  const PREFIX = 'duq_';

  /**
   * Save a value to localStorage with the duq prefix.
   */
  function save(key, value) {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.warn('duq-persist: Failed to save', key, e);
      return false;
    }
  }

  /**
   * Load a value from localStorage.
   */
  function load(key, fallback) {
    try {
      const raw = localStorage.getItem(PREFIX + key);
      if (raw === null) return fallback;
      return JSON.parse(raw);
    } catch (e) {
      console.warn('duq-persist: Failed to load', key, e);
      return fallback;
    }
  }

  /**
   * Remove a saved key from localStorage.
   */
  function remove(key) {
    try {
      localStorage.removeItem(PREFIX + key);
    } catch (e) { /* ignore */ }
  }

  /**
   * Debounce helper: returns a function that delays invoking `fn`
   * until `delay` ms have elapsed since the last invocation.
   */
  function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        fn.apply(this, args);
        timer = null;
      }, delay);
    };
  }

  // Expose globally
  window.duqPersist = { save, load, remove, debounce, PREFIX };

})();
