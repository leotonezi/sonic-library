export const API_ENDPOINTS = {
  BOOKS: '/books',
  USER_BOOKS: '/user-books',
  AUTH: '/auth',
  REVIEWS: '/reviews',
  RECOMMENDATIONS: '/recommendations',
  UPLOAD: '/upload',
  EXTERNAL_BOOKS: '/books/search-external',
  POPULAR_BOOKS: '/books/popular',
} as const;

export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  POPULAR_BOOKS_PAGE_SIZE: 12,
} as const;

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  BOOKS: '/books',
  LIBRARY: '/library',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  RECOMMENDATIONS: '/recommendation',
} as const;

export const BOOK_STATUS = {
  WANT_TO_READ: 'want_to_read',
  CURRENTLY_READING: 'currently_reading',
  READ: 'read',
} as const;

export const RATING_SCALE = {
  MIN: 1,
  MAX: 5,
} as const;