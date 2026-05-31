import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Merriweather } from "next/font/google";
import "./globals.css";
import { AuthHydrator } from "@/components/auth-hydrator";
import { Toaster } from 'sonner';


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const merriweather = Merriweather({
  variable: "--font-merriweather",
  subsets: ["latin"],
  weight: ["400", "700"],
});


export const metadata: Metadata = {
  title: "Sonic Library 📖",
  description: "Your fastest digital library!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <link rel="icon" href="/sonic-library.ico" />
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${merriweather.variable} antialiased`}
      >
        <AuthHydrator />
          {children}
        <Toaster />

        <footer className="bg-blue-900 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-blue-200 text-center text-sm">
              © {new Date().getFullYear()} Sonic Library. All rights reserved.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
