// nodered/tests/harness.js
const fs = require('fs');
const path = require('path');

exports.load = function(relPath) {
  const fullPath = path.resolve(__dirname, '..', relPath);
  const code = fs.readFileSync(fullPath, 'utf8');
  return new Function('msg', 'flow', 'node', 'env', code);
};

exports.mkFlow = function() {
  const store = new Map();
  return {
    get: function(key) { return store.get(key); },
    set: function(key, val) { store.set(key, val); }
  };
};

exports.node = {
  warn: function() {},
  log: function() {},
  error: function() {}
};

exports.mkEnv = function(dict = {}) {
  return {
    get: function(key) { return dict[key]; }
  };
};
