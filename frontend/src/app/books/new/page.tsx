'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export default function NewBookPage() {
  const [author, setAuthor] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/books/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ author, title, description }),
    });

    if (res.ok) {
      toast.success('Book created!');
      
      const book = await res.json();
      router.push(`/books/${book.id}`);
    } else {
      alert('Failed to create book.');
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
            className="mt-1 w-full border border-blue-600 text-blue-300 focus:border-blue-400 focus:outline-none px-3 py-2 rounded"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-400">Title</label>
          <input
            type="text"
            className="mt-1 w-full border border-blue-600 text-blue-300 focus:border-blue-400 focus:outline-none px-3 py-2 rounded"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-400">Description</label>
          <textarea
            className="mt-1 w-full border border-blue-600 text-blue-300 focus:border-blue-400 focus:outline-none px-3 py-2 rounded"
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