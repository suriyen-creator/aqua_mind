import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AquaMind AI",
  description: "ระบบประเมินความเสี่ยงแพลงก์ตอนบลูมชายฝั่ง",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
