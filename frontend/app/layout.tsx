import "./globals.css";

export const metadata = {
  title: "Algory",
  description: "Quantitative infrastructure platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-zinc-900 font-mono">
        {children}
      </body>
    </html>
  );
}