// Suppress React act() warnings - this must run before React loads
// Store original console methods before any overrides
const originalError = console.error;
const originalWarn = console.warn;

// Override console.error to filter act() warnings
console.error = (...args) => {
  // Convert all args to string and check if it's an act() warning
  const message = args
    .map((arg) => {
      if (typeof arg === 'string') return arg;
      if (arg?.message) return arg.message;
      if (arg?.stack) return arg.stack;
      try {
        return String(arg);
      } catch {
        return '';
      }
    })
    .join(' ')
    .toLowerCase();

  // Suppress act() related warnings
  if (
    message.includes('not wrapped in act') ||
    (message.includes('an update to') && message.includes('inside a test')) ||
    message.includes('act(...)') ||
    (message.includes('warning') && message.includes('act'))
  ) {
    return; // Suppress this warning
  }

  // Otherwise, call original console.error
  originalError.apply(console, args);
};

// Override console.warn similarly
console.warn = (...args) => {
  const message = args
    .map((arg) => {
      if (typeof arg === 'string') return arg;
      try {
        return String(arg);
      } catch {
        return '';
      }
    })
    .join(' ')
    .toLowerCase();

  if (
    message.includes('not wrapped in act') ||
    (message.includes('an update to') && message.includes('inside a test')) ||
    message.includes('act(...)')
  ) {
    return; // Suppress this warning
  }

  originalWarn.apply(console, args);
};

// Also try to disable React's internal act() environment flag
// This is a React internal mechanism, may not work in all versions
try {
  if (typeof global !== 'undefined') {
    global.IS_REACT_ACT_ENVIRONMENT = false;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.IS_REACT_ACT_ENVIRONMENT = false;
  }
} catch {
  // Ignore if setting fails
}

