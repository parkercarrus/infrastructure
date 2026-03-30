import PortfolioClient from "./PortfolioClient";

export const runtime = "nodejs";

// Revalidate the page data every hour
export const revalidate = 3600;

const SHEET_URL =
  "https://docs.google.com/spreadsheets/d/1JOmzegYf0kGxDcjej0Fx_RCuFVoaOxobEnDsptjTJA8/export?format=csv&gid=595987006";

export type Position = {
  ticker: string;
  entryDate: string;
  avgCost: number;
  numShares: number;
  costBasis: number;
  daysHeld: number;
  weight: number;
};

// Minimal RFC 4180-compatible CSV row parser
function parseCSVLine(line: string): string[] {
  const cells: string[] = [];
  let inQuote = false;
  let current = "";

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      // escaped quote inside quoted field
      if (inQuote && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuote = !inQuote;
      }
    } else if (ch === "," && !inQuote) {
      cells.push(current.trim());
      current = "";
    } else {
      current += ch;
    }
  }
  cells.push(current.trim());
  return cells;
}

// Parse date strings like "3/20/23" or "10/21/2025" → days from that date to today
function daysSince(dateStr: string): number {
  if (!dateStr) return 0;
  const parts = dateStr.split("/");
  if (parts.length !== 3) return 0;
  const month = parseInt(parts[0], 10) - 1;
  const day = parseInt(parts[1], 10);
  let year = parseInt(parts[2], 10);
  if (year < 100) year += 2000;
  const then = new Date(year, month, day).getTime();
  if (Number.isNaN(then)) return 0;
  return Math.max(0, Math.floor((Date.now() - then) / 86_400_000));
}

async function getPositions(): Promise<Position[]> {
  try {
    const res = await fetch(SHEET_URL, { next: { revalidate: 3600 } });
    if (!res.ok) return [];

    const csv = await res.text();
    const lines = csv.trim().split("\n");
    const rows = lines.map(parseCSVLine);

    // Find the header row that contains a "ticker" column
    let headerRowIdx = -1;
    let colTicker = -1;

    for (let i = 0; i < rows.length; i++) {
      for (let j = 0; j < rows[i].length; j++) {
        const normalised = rows[i][j]
          .replace(/[^a-zA-Z0-9]/g, "")
          .toLowerCase();
        if (normalised === "ticker") {
          headerRowIdx = i;
          colTicker = j;
          break;
        }
      }
      if (headerRowIdx >= 0) break;
    }

    if (headerRowIdx < 0) return [];

    // Identify the remaining relevant columns from the header row
    const header = rows[headerRowIdx];
    let colDate = -1;
    let colCost = -1;
    let colShares = -1;

    for (let j = 0; j < header.length; j++) {
      if (j === colTicker) continue;
      const cell = header[j]
        .replace(/[^a-zA-Z0-9 ]/g, "")
        .toLowerCase()
        .trim();
      if (cell.includes("date") || cell.includes("entry")) colDate = j;
      else if (cell.includes("cost") || cell.includes("avg")) colCost = j;
      else if (cell.includes("share") || cell.startsWith("#") || cell === "of shares") colShares = j;
    }

    const raw: Omit<Position, "weight">[] = [];

    for (let i = headerRowIdx + 1; i < rows.length; i++) {
      const row = rows[i];

      const ticker = (colTicker >= 0 ? row[colTicker] ?? "" : "")
        .replace(/[^A-Za-z.]/g, "")
        .toUpperCase()
        .trim();
      if (!ticker) continue;

      const entryDate =
        colDate >= 0 ? (row[colDate] ?? "").trim() : "";

      const avgCostRaw = (colCost >= 0 ? row[colCost] ?? "0" : "0")
        .replace(/[$,]/g, "")
        .trim();
      const numSharesRaw = (
        colShares >= 0 ? row[colShares] ?? "0" : "0"
      )
        .replace(/[,]/g, "")
        .trim();

      const avgCost = parseFloat(avgCostRaw) || 0;
      const numShares = parseInt(numSharesRaw, 10) || 0;
      if (avgCost === 0 || numShares === 0) continue;

      raw.push({
        ticker,
        entryDate,
        avgCost,
        numShares,
        costBasis: avgCost * numShares,
        daysHeld: daysSince(entryDate),
      });
    }

    const totalInvested = raw.reduce((s, p) => s + p.costBasis, 0);

    return raw.map((p) => ({
      ...p,
      weight: totalInvested > 0 ? p.costBasis / totalInvested : 0,
    }));
  } catch {
    return [];
  }
}

export default async function PortfolioPage() {
  const positions = await getPositions();

  const totalInvested = positions.reduce((s, p) => s + p.costBasis, 0);
  const avgPositionSize =
    positions.length > 0 ? totalInvested / positions.length : 0;
  const largest = positions.reduce<Position | null>(
    (best, p) => (!best || p.costBasis > best.costBasis ? p : best),
    null
  );

  return (
    <main className="min-h-screen bg-white text-zinc-900 font-mono">
      <PortfolioClient
        positions={positions}
        totalInvested={totalInvested}
        avgPositionSize={avgPositionSize}
        largestPosition={largest}
      />
    </main>
  );
}
