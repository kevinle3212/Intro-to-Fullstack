import { useEffect, useMemo, useState } from "react";
import "./App.css";

type Quote = {
  timestamp: string;
  symbol: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

type SeriesResponse = {
  status: string;
  ticker: string;
  count: number;
  data: Quote[];
};

type SummaryResponse = {
  status: string;
  ticker: string;
  response?: string;
  message?: string;
};

const API_BASE = "http://localhost:4200";

type Stat = {
  mean: number;
  median: number;
  std: number;
};

type StatMap = Record<"open" | "high" | "low" | "close", Stat>;

function computeStats(data: Quote[]): StatMap | null {
  if (!data.length) return null;
  const fields: Array<keyof StatMap> = ["open", "high", "low", "close"];

  const result = {} as StatMap;

  for (const field of fields) {
    const values = data.map((d) => Number(d[field])).filter((v) => !Number.isNaN(v));
    if (!values.length) {
      result[field] = { mean: NaN, median: NaN, std: NaN };
      continue;
    }
    const mean = values.reduce((acc, v) => acc + v, 0) / values.length;
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    const median =
      sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    const variance =
      values.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / values.length;
    const std = Math.sqrt(variance);
    result[field] = { mean, median, std };
  }

  return result;
}

function LineChart({ data }: { data: Quote[] }) {
  const points = useMemo(() => {
    if (!data.length) return "";
    const sorted = [...data].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    const closes = sorted.map((d) => Number(d.close));
    const times = sorted.map((d) => new Date(d.timestamp).getTime());

    const minClose = Math.min(...closes);
    const maxClose = Math.max(...closes);
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);

    const normalizeX = (t: number) =>
      maxTime === minTime ? 0 : ((t - minTime) / (maxTime - minTime)) * 100;
    const normalizeY = (c: number) =>
      maxClose === minClose ? 50 : 100 - ((c - minClose) / (maxClose - minClose)) * 100;

    return sorted
      .map((d) => `${normalizeX(new Date(d.timestamp).getTime())},${normalizeY(d.close)}`)
      .join(" ");
  }, [data]);

  if (!points) {
    return (
      <div className="empty-chart">
        <p>No data to plot yet.</p>
      </div>
    );
  }

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="chart">
      <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#6bdcff" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#1e2d3f" stopOpacity="0.2" />
        </linearGradient>
      </defs>
      <polyline fill="none" stroke="url(#lineGradient)" strokeWidth="1.5" points={points} />
      <polyline
        fill="url(#lineGradient)"
        stroke="none"
        points={`${points} 100,100 0,100`}
        opacity={0.18}
      />
    </svg>
  );
}

function StatCard({ label, stat }: { label: string; stat: Stat }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-row">
        <span>Mean</span>
        <strong>{stat.mean.toFixed(2)}</strong>
      </div>
      <div className="stat-row">
        <span>Median</span>
        <strong>{stat.median.toFixed(2)}</strong>
      </div>
      <div className="stat-row">
        <span>Std</span>
        <strong>{stat.std.toFixed(2)}</strong>
      </div>
    </div>
  );
}

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [series, setSeries] = useState<Quote[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stats = useMemo(() => computeStats(series), [series]);

  const fetchData = async (symbol: string) => {
    setLoading(true);
    setError(null);
    try {
      const [seriesRes, summaryRes] = await Promise.all([
        fetch(`${API_BASE}/stock/${symbol}/last-month?limit=200`),
        fetch(`${API_BASE}/stock/${symbol}/openapi-prompt`),
      ]);

      if (!seriesRes.ok) {
        throw new Error(`Series request failed (${seriesRes.status})`);
      }
      const seriesJson = (await seriesRes.json()) as SeriesResponse;
      setSeries(seriesJson.data || []);

      if (!summaryRes.ok) {
        throw new Error(`AI summary request failed (${summaryRes.status})`);
      }
      const summaryJson = (await summaryRes.json()) as SummaryResponse;
      setSummary(summaryJson.response || "No summary available.");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      setSeries([]);
      setSummary("");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(ticker);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    fetchData(ticker.trim().toUpperCase());
  };

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Fullstack Dashboard</p>
          <h1>
            {ticker.toUpperCase()} performance
            <span className="accent"> — last month</span>
          </h1>
          <p className="subhead">
            Price curve, distribution stats, and AI-generated narrative — all in one view.
          </p>
        </div>
        <form className="ticker-form" onSubmit={handleSubmit}>
          <label htmlFor="ticker">Ticker</label>
          <div className="input-row">
            <input
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="AAPL"
              maxLength={8}
            />
            <button type="submit" disabled={loading}>
              {loading ? "Loading..." : "Load"}
            </button>
          </div>
        </form>
      </header>

      {error ? (
        <div className="error-banner">⚠️ {error}</div>
      ) : (
        <>
          <section className="panel">
            <div className="panel-head">
              <h2>Price action</h2>
              <span className="pill">
                {series.length ? `${series.length} bars` : "No data"}
              </span>
            </div>
            <LineChart data={series} />
          </section>

          <section className="panel">
            <div className="panel-head">
              <h2>Distribution snapshot</h2>
              <span className="pill">open / high / low / close</span>
            </div>
            {!stats ? (
              <p className="muted">No stats yet. Load a ticker to compute metrics.</p>
            ) : (
              <div className="stats-grid">
                <StatCard label="Open" stat={stats.open} />
                <StatCard label="High" stat={stats.high} />
                <StatCard label="Low" stat={stats.low} />
                <StatCard label="Close" stat={stats.close} />
              </div>
            )}
          </section>

          <section className="panel">
            <div className="panel-head">
              <h2>AI summary</h2>
              <span className="pill">Generated live</span>
            </div>
            {loading && !summary ? (
              <p className="muted">Requesting summary…</p>
            ) : (
              <p className="summary">{summary || "No summary returned."}</p>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default App;
