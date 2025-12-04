"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type Point = {
  index: number;
  price: number;
};

export default function Body() {
  const router = useRouter();

  // -----------------------------
  // MASTER DATA
  // -----------------------------
  function generateRandomWalk(points: number) {
    let data: Point[] = [];
    let price = 100;
    for (let i = 0; i < points; i++) {
      price += (Math.random() - 0.5) * 2;
      data.push({ index: i, price: Number(price.toFixed(2)) });
    }
    return data;
  }

  const baseDataSize = 2000;
const [baseData, setBaseData] = useState<Point[]>([]);

// generate dataset only in browser
useEffect(() => {
  setBaseData(generateRandomWalk(baseDataSize));
}, []);


  // -----------------------------
  // STATE / RANGES
  // -----------------------------
  const [range, setRange] = useState("1D");
  const [viewData, setViewData] = useState<Point[]>(baseData);

  const RANGE_POINTS: Record<string, number> = {
    "1D": 30,
    "1W": 80,
    "1M": 200,
    "6M": 600,
    "1Y": 1000,
    "5Y": baseDataSize,
  };

  useEffect(() => {
    const pts = RANGE_POINTS[range] ?? baseDataSize;
    const sliced = baseData.slice(-pts);
    setViewData(sliced);
  }, [range, baseData]);

  // -----------------------------
  // CHART SIZING & SCALES
  // -----------------------------
  const width = 700;
  const height = 500;

  const minPrice = viewData.length ? Math.min(...viewData.map((p) => p.price)) : 0;
  const maxPrice = viewData.length ? Math.max(...viewData.map((p) => p.price)) : 0;
  const priceRange = maxPrice - minPrice || 1;

  const scaleY = (price: number) => height - ((price - minPrice) / priceRange) * height;
  const xForIndex = (i: number) =>
    (i / Math.max(1, viewData.length - 1)) * width;

  // Build polyline points and circles coordinates using normalized index (0..n-1)
  const pointsString =
    viewData.length > 0
      ? viewData
          .map((p, i) => `${xForIndex(i)},${scaleY(p.price)}`)
          .join(" ")
      : "";

  // Decide whether to render circles for every point (avoid DOM bloat)
  const MAX_CIRCLES = 600; // cap of direct circle elements
  const renderEvery = viewData.length > MAX_CIRCLES ? Math.ceil(viewData.length / MAX_CIRCLES) : 1;

  // Latest price (kept for highlight logic but not shown as badge)
  const latestPrice = viewData.length ? viewData[viewData.length - 1].price : null;

  // -----------------------------
  // RENDER
  // -----------------------------
  return (
    <div className="flex flex-col bg-white font-sans flex-grow">

      {/* Top Section */}
      <div className="flex flex-col flex-grow justify-center items-center p-10">

        {/* Title */}
        <h1 className="text-4xl font-bold text-gray-800 mb-4">S&P 500 Overview</h1>

        {/* Chart Box */}
        <div className="rounded-lg shadow-md border border-gray-300 bg-white p-3 flex w-[700px] h-[500px] relative">

          {/* Y-axis labels */}
          <div className="flex flex-col justify-between mr-3 text-sm text-gray-700 select-none">
            {Array.from({ length: 6 }).map((_, i) => {
              const percent = 1 - i / 5;
              const value = (minPrice + priceRange * percent).toFixed(2);
              return <span key={i}>{value}</span>;
            })}
          </div>

          {/* SVG Chart */}
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
            {/* Grid lines */}
            {Array.from({ length: 6 }).map((_, i) => {
              const y = (i / 5) * height;
              return <line key={i} x1="0" y1={y} x2={width} y2={y} stroke="#eee" strokeWidth={1} />;
            })}

            {/* Polyline */}
            <polyline fill="none" stroke="#111827" strokeWidth={2} points={pointsString} />

            {/* Circles for data points (sampled if too many) */}
            {viewData.map((p, i) => {
              if (i % renderEvery !== 0) return null;
              const cx = xForIndex(i);
              const cy = scaleY(p.price);
              return <circle key={i} cx={cx} cy={cy} r={2} fill="#111827" />;
            })}

            {/* Highlight last point */}
            {viewData.length > 0 && (() => {
              const i = viewData.length - 1;
              const cp = { cx: xForIndex(i), cy: scaleY(viewData[i].price) };
              return (
                <>
                  <circle cx={cp.cx} cy={cp.cy} r={4} fill="#10b981" stroke="#065f46" strokeWidth={1} />
                  {/* small halo */}
                  <circle cx={cp.cx} cy={cp.cy} r={8} fill="none" stroke="#10b981" strokeOpacity={0.12} strokeWidth={2} />
                </>
              );
            })()}
          </svg>
        </div>
      </div>

      {/* Bottom Buttons */}
      <div className="flex w-full h-[100px] items-center justify-center bg-gray-100 border-t border-gray-300">
        <div className="flex gap-4">
          {["1D", "1W", "1M", "6M", "1Y", "5Y"].map((label) => (
            <button
              key={label}
              onClick={() => setRange(label)}
              className={`px-6 py-3 text-lg font-medium rounded-md border transition ${
                range === label ? "bg-black text-white border-black" : "bg-gray-300 text-black border-gray-400 hover:bg-gray-400"
              }`}
            >
              {label}
            </button>
          ))}

          <button
            onClick={() => router.push("/search")}
            className="px-8 py-3 text-xl font-semibold text-white rounded-md bg-gray-800 hover:bg-gray-700 transition"
          >
            Search Stocks
          </button>
        </div>
      </div>
    </div>
  );
}
