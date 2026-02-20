import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-white text-zinc-900 font-mono">
      {/* Top Navigation Bar */}
      <nav className="w-full border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 h-14 flex items-center justify-between">
          <div className="text-sm font-semibold tracking-tight">
            Algory Capital Quantitative Investments
          </div>

          <div className="flex items-center gap-6 text-sm">
            <Link
              href="/"
              className="hover:text-black text-zinc-600 transition"
            >
              Home
            </Link>

            <Link
              href="/dashboard"
              className="hover:text-black text-zinc-600 transition"
            >
              Dashboard
            </Link>

            <a
              href="https://www.algorycapital.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-black text-zinc-600 transition"
            >
              Algory Capital
            </a>
          </div>
        </div>
      </nav>

      <div>{children}</div>
    </div>
  );
}