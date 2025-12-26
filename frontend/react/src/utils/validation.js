/**
 * Validate email format
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * Returns error message if invalid, null if valid
 */
export const validatePassword = (password, t) => {
  if (password.length < 8) return t("register.error_password_length");
  if (!/[A-Z]/.test(password)) return t("register.error_password_uppercase");
  if (!/[a-z]/.test(password)) return t("register.error_password_lowercase");
  if (!/\d/.test(password)) return t("register.error_password_number");
  if (!/[^\w\s]/.test(password)) return t("register.error_password_symbol");
  return null; // valid
};

/**
 * Validate date range
 */
export const validateDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return false;
  return new Date(startDate) <= new Date(endDate);
};

