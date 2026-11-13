import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CYBERQUEST",
  description: "Learn. Hack. Defend. Master.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
