import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "ChronoColor 4K AI — Transform B&W Videos into 4K Color Masterpieces",
  description:
    "AI-powered video colorization platform. Transform black & white footage into stunning 4K HDR color using 15+ AI models for restoration, super-resolution, and cinematic colorization.",
  keywords: [
    "video colorization",
    "AI",
    "4K upscaling",
    "black and white",
    "HDR",
    "restoration",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-bg-primary text-text-primary">
        {children}
      </body>
    </html>
  );
}
