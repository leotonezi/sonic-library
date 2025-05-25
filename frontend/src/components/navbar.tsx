"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { Menu } from "lucide-react";
import { useRouter } from "next/navigation";

export default function NavBar() {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();

  if (!user) return null;

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <nav className="shadow-md flex bg-[#0a1f44] justify-between h-16 px-4">
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

      <div className="flex gap-4 relative items-center">
        <Link
          href="/books"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Books
        </Link>
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
        <Link
          href="/users"
          className="flex items-center justify-center h-full px-4 hover:bg-[#004aad] transition-all duration-500 ease-in-out text-white"
        >
          Users
        </Link>

        {/* 👤 User menu dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen((prev) => !prev)}
            className="flex items-center justify-center h-full px-4 cursor-pointer text-white"
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
