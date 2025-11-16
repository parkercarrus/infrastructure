"use client";

import Link from "next/link";
import { Separator } from "@/components/ui/separator";

function H2({ children }: { children: React.ReactNode }) {
  return <h2 className="text-2xl font-semibold tracking-tight mb-2">{children}</h2>;
}
function H3({ children }: { children: React.ReactNode }) {
  return <h3 className="text-lg font-semibold mt-6 mb-2">{children}</h3>;
}
function P({ children }: { children: React.ReactNode }) {
  return <p className="text-muted-foreground">{children}</p>;
}
function UL({ children }: { children: React.ReactNode }) {
  return <ul className="list-disc pl-6 space-y-1 text-muted-foreground">{children}</ul>;
}
function OL({ children }: { children: React.ReactNode }) {
  return <ol className="list-decimal pl-6 space-y-2 text-muted-foreground">{children}</ol>;
}
function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="rounded bg-muted px-1 py-0.5 font-mono text-sm text-foreground">
      {children}
    </code>
  );
}

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-background text-foreground px-6 py-8 font-sans antialiased">
      {/* Header */}
      <div className="border border-black rounded-lg p-4 flex justify-between items-end mb-12 bg-background">
        <h1 className="text-3xl font-semibold tracking-tight">About</h1>
        <nav className="space-x-6">
          <Link href="/" className="hover:underline">Home</Link>
          <Link href="/docs" className="hover:underline">API</Link>
          <Link href="/dashboard" className="hover:underline">Simulation</Link>
        </nav>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto text-[17px] leading-8 sm:text-[18px] sm:leading-9 space-y-8">
        <section className="space-y-3">
          <H2>About</H2>
          <P>
            Algory Capital QI About Page
          </P>
        </section>
      </div>
    </main>
  );
}
