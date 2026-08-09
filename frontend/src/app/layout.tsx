import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SkillProof — Adaptive AI Technical Interviewer",
  description: "Know it. Show it. Prove it. Build the interviewer, not the interview.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0b0f19] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
