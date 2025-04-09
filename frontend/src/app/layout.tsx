import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Merriweather, Playfair_Display, Lora, EB_Garamond } from "next/font/google";
import "./globals.css";
import NavBar from "@/components/navbar";
import { Toaster } from 'sonner';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const merriwether = Merriweather({
  variable: "--font-merriweather",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const garamond = EB_Garamond({
  variable: "--font-garamond",
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
        className={`${geistSans.variable} ${geistMono.variable} ${merriwether.variable} ${playfair.variable} ${lora.variable} ${garamond.variable} antialiased`}
      >
        <NavBar/>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
