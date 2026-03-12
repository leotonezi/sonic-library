// Test user data
export const testUser = {
  email: 'test@e2etest.example.com',
  password: 'TestPassword123!',
  name: 'Test User',
};

export const adminUser = {
  email: 'admin@e2etest.example.com',
  password: 'AdminPassword123!',
  name: 'Admin User',
};

export const invalidUser = {
  email: 'invalid@example.com',
  password: 'wrongpassword',
};

// API URL for test environment
export const API_URL = process.env.API_URL || 'http://localhost:8001';
