import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nutrigenomics Analysis",
  description: "Get personalized nutrition recommendations based on your genetics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
