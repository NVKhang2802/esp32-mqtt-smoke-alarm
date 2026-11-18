// web/util.js
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    const exports = factory();
    root.Util = exports;
    root.escapeHtml = exports.escapeHtml;
    root.safeLevelClass = exports.safeLevelClass;
  }
}(typeof self !== 'undefined' ? self : this, function () {
  function escapeHtml(v) {
    return String(v === null || v === undefined ? '' : v)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  const LEVELS = ['INFO', 'WARN', 'CRITICAL', 'SUCCESS'];
  function safeLevelClass(lv) {
    return (LEVELS.includes(lv) ? 'lvl-' + lv.toLowerCase() : 'lvl-info');
  }

  return {
    escapeHtml: escapeHtml,
    safeLevelClass: safeLevelClass
  };
}));
