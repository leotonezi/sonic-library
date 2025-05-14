'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { BOOK_GENRES } from '@/utils/enums'; // Adjust the path based on your project structure
import { apiPost } from '@/utils/api';

export default function NewBookPage() {
  const [author, setAuthor] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [genre, setGenre] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await apiPost<{ id: number; author: string; title: string; description: string; genre: string }>(
        '/books/',
        { author, title, description, genre }
      );
      console.log(response)
      toast.success('Book created!');
      router.push(`/books/${response.id}`);
    } catch (err) {
      toast.error('Failed to create book.');
      console.error('Book creation failed:', err);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-blue-900 border border-blue-600 rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-4 text-blue-500">Add a New Book</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-blue-400">Author</label>
          <input
            type="text"
            className="input-primary"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-400">Title</label>
          <input
            type="text"
            className="input-primary"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-400">Genre</label>
          <select
            className="input-primary"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            required
          >
            <option value="">Select a Genre</option>
            {BOOK_GENRES.map((genreOption: { label: string, value: string }) => (
              <option 
                key={genreOption.value} 
                value={genreOption.label}
              >
                {genreOption.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-400">Description</label>
          <textarea
            className="input-primary"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            required
          />
        </div>
        <button
          type="submit"
          className="btn-primary"
        >
          Create Book
        </button>
      </form>
    </div>
  );
}
