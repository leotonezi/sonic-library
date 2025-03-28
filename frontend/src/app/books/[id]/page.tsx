// app/books/[id]/page.tsx
export const revalidate = 60; // ISR every 60 seconds
export const dynamicParams = true; // allow dynamic paths not returned from generateStaticParams

interface Book {
  id: string;
  title: string;
  author: string;
  description?: string;
}

// We're not pre-generating any paths; they will be generated on-demand
export async function generateStaticParams() {
  return []; // this enables runtime ISR generation
}

export default async function BookPage({
  params,
}: {
  params: { id: string };
}) {
  const res = await fetch(`http://localhost:8000/books/${params.id}`, {
    next: { revalidate: 60 },
  });

  if (!res.ok) {
    // Optionally handle 404
    throw new Error('Book not found');
  }

  const book: Book = await res.json();

  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-2">{book.title}</h1>
      <p className="text-gray-600 text-sm mb-4">By {book.author}</p>
      {book.description && <p>{book.description}</p>}
    </main>
  );
}