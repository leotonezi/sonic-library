# Pagination Implementation

This document describes the pagination features implemented in the Sonic Library API.

## Overview

Pagination has been added to improve performance and user experience when dealing with large datasets. The implementation provides consistent pagination metadata across all endpoints.

## Pagination Response Format

All paginated endpoints return a response with the following structure:

```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 50,
    "page_size": 10,
    "has_next": true,
    "has_previous": false,
    "start_index": 0,
    "end_index": 10
  },
  "message": "Success",
  "status": "ok"
}
```

## Pagination Parameters

- `page`: Page number (default: 1, minimum: 1)
- `page_size`: Number of items per page (default: 10, minimum: 1, maximum: 100)

## Endpoints with Pagination

### 1. User Books Pagination

**Endpoint**: `GET /api/v1/user-books/my-books/paginated`

**Parameters**:
- `page`: Page number
- `page_size`: Items per page
- `status`: Optional filter by reading status (TO_READ, READING, READ)

**Example**:
```bash
GET /api/v1/user-books/my-books/paginated?page=1&page_size=10&status=TO_READ
```

### 2. Books Listing Pagination

**Endpoint**: `GET /api/v1/books/`

**Parameters**:
- `page`: Page number
- `page_size`: Items per page
- `search`: Optional search term
- `genre`: Optional genre filter

**Example**:
```bash
GET /api/v1/books/?page=2&page_size=20&search=python&genre=fiction
```

### 3. Google Books Search Pagination

**Endpoint**: `GET /api/v1/books/search-external`

**Parameters**:
- `q`: Search query (required)
- `max_results`: Maximum results per page (default: 10, max: 40)
- `page`: Page number

**Note**: Google Books API has a limitation of 40 results per page.

**Example**:
```bash
GET /api/v1/books/search-external?q=python&page=1&max_results=20
```

### 4. Popular Books Pagination

**Endpoint**: `GET /api/v1/books/popular`

**Parameters**:
- `max_results`: Maximum results per page (default: 12, max: 40)
- `page`: Page number

**Example**:
```bash
GET /api/v1/books/popular?page=1&max_results=20
```

## Implementation Details

### Database-Level Pagination

For database queries, pagination is implemented at the SQL level using `OFFSET` and `LIMIT`:

```python
# Calculate offset
offset = (page - 1) * page_size

# Get total count
total_count = query.count()

# Get paginated results
books = query.offset(offset).limit(page_size).all()
```

### Google Books API Pagination

For Google Books API, pagination uses the `startIndex` parameter:

```python
params = {
    "q": query,
    "maxResults": max_results_per_page,
    "startIndex": start_index,
}
```

### Caching with Pagination

Popular books are cached and pagination is applied to cached results:

```python
# Apply pagination to cached results
start_index = (page - 1) * max_results
end_index = start_index + max_results
paginated_books = cached_books[start_index:end_index]
```

## Performance Considerations

1. **Database Queries**: Pagination is implemented at the database level to avoid loading unnecessary data
2. **Indexing**: Ensure proper database indexes on frequently queried fields
3. **Caching**: Popular books are cached to reduce API calls to Google Books
4. **Page Size Limits**: Maximum page size is limited to prevent performance issues

## Error Handling

- Invalid page numbers (less than 1) return 422 Unprocessable Entity
- Page sizes outside allowed range return 422 Unprocessable Entity
- Empty pages return empty data array with appropriate pagination metadata

## Testing

Pagination functionality is tested in `backend/tests/test_pagination.py` with comprehensive test cases covering:

- Basic pagination functionality
- Status filtering with pagination
- Edge cases (empty results, last page, etc.)
- Google Books API pagination structure
- Popular books pagination

## Future Enhancements

1. **Cursor-based pagination**: For better performance with large datasets
2. **Infinite scroll support**: Additional metadata for frontend implementation
3. **Sorting options**: Allow sorting by different fields with pagination
4. **Advanced filtering**: More complex filtering options with pagination 