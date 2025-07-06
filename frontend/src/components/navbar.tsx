// components/NavBar.tsx
"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { Menu, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useSearchBookStore } from "@/store/useSearchBookStore";
import { toast } from "sonner";

export default function NavBar() {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [genreInput, setGenreInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);

  const searchQuery = useSearchBookStore((state) => state.searchQuery);
  const setSearchQuery = useSearchBookStore((state) => state.setSearchQuery);
  const fetchExternalBooks = useSearchBookStore(
    (state) => state.fetchExternalBooks,
  );

  // Don't render navbar if still loading or no user
  if (isLoading || !user) {
    return null;
  }

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      await fetchExternalBooks(genreInput);
      toast.success("Search Complete!!!");
      router.push("/books");
    } catch (error) {
      console.error("Search failed:", error);
      toast.error("Search failed. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <nav className="shadow-md flex bg-[#0a1f44] h-16 px-4 items-center">
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

      {/* Centered Search Bar with Genre Input */}
      <div className="flex-grow flex justify-center">
        <div className="flex items-center gap-2">
          {/* Genre Input */}
          <div className="flex items-center bg-blue-950 h-10 border border-blue-700 rounded-md">
            <input
              type="text"
              value={genreInput}
              onChange={(e) => setGenreInput(e.target.value)}
              placeholder="Type Genre..."
              className="pl-2 pr-2 py-1 w-32 rounded-md bg-transparent text-white placeholder-blue-300 focus:outline-none text-sm"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSearch();
              }}
              />
          </div>

          {/* Search Input */}
          <div className="flex items-center bg-blue-950 h-10 w-100 border border-blue-700 rounded-md">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search Google Books..."
              className="pl-2 pr-2 py-1 w-100 rounded-md bg-transparent text-white placeholder-blue-300 focus:outline-none text-sm"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSearch();
              }}
            />
          </div>
          <Search
            size={20}
            className={`transition duration-300 cursor-pointer mx-2 ${
              isSearching 
                ? 'text-orange-400 animate-pulse' 
                : 'text-white hover:text-orange-300'
            }`}
            onClick={handleSearch}
          />
        </div>
      </div>

      {/* Right-aligned Navigation Links and User Menu */}
      <div className="flex h-full">
        <Link
          href={`/library/`}
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          My Library
        </Link>
        <Link
          href="/recommendation"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Recommend
        </Link>
        {/* User menu dropdown */}
        <div className="relative h-full">
          <button
            onClick={() => setDropdownOpen((prev) => !prev)}
            className="flex items-center justify-center h-full px-4 cursor-pointer text-white hover:bg-[#004aad] transition-all duration-500 ease-in-out"
          >
            <Menu />
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 top-full mt-1 w-32 bg-white rounded shadow text-black z-50">
              <Link
                href="/profile"
                className="block w-full px-4 py-2 text-left hover:bg-gray-100 cursor-pointer"
                onClick={() => setDropdownOpen(false)}
              >
                Profile
              </Link>
              <Link
                href="/settings"
                className="block w-full px-4 py-2 text-left hover:bg-gray-100 cursor-pointer border-t"
                onClick={() => setDropdownOpen(false)}
              >
                Settings
              </Link>
              <button
                onClick={() => {
                  handleLogout();
                  setDropdownOpen(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 cursor-pointer border-t"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
