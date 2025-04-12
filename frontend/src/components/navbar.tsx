import Link from "next/link";
import Image from "next/image";

export default function NavBar() {
  return (
    <nav className="shadow-md flex bg-[#0a1f44] justify-between h-16">
      <Link href="/" className="flex items-center h-full">
        <Image
          src="/sonic-library-logo.png"
          priority
          alt="Home Logo"
          width={80}
          height={80}
          className="object-contain"
        />
      </Link>
      <div className="flex gap-4">
        <Link
          href="/books"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Books
        </Link>
        <Link
          href="/recommendation"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Recommend
        </Link>
        <Link
          href="/users"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Users
        </Link>
        <Link
          href="/login"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Login
        </Link>
      </div>
    </nav>
  );
}


