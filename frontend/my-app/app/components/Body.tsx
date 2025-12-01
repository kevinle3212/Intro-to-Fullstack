"use client";
import { useRouter } from "next/navigation";

export default function Body() {
  const router = useRouter();

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-white to-gray-100 font-sans">
      {/* Top Section */}
      <div className="flex flex-1 p-6 gap-6">
        {/* Image Box */}
        <div className="rounded-2xl overflow-hidden shadow-xl w-[550px] h-[500px]">
          <img
            src="stocks.gif"
            alt="Stocks Animation"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Stock List */}
        <div className="flex flex-col flex-1 bg-white border border-gray-300 rounded-2xl shadow-xl overflow-hidden h-[500px]">
          <p className="text-[42px] font-semibold text-gray-800 py-4 border-b border-gray-300">
            Top Stocks
          </p>

          <div className="flex flex-col overflow-y-auto divide-y divide-gray-200">
            {[1, 2, 3, 4].map((item) => (
              <div
                key={item}
                className="h-[120px] flex justify-between items-center px-10 hover:bg-gray-50 transition"
              >
                <p className="text-[26px] text-gray-700 font-medium">Stock</p>
                <img
                  src="stocks.gif"
                  alt="Stocks Animation"
                  className="w-48 h-20 opacity-90 hover:opacity-75 transition"
                />
                <p className="text-[26px] text-gray-700 font-medium">Value</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Buttons */}
      <div className="flex w-full h-[100px] items-center justify-center bg-white border-t">
      <div className="flex gap-4">
        {["Day", "Week", "Month", "Year", "5 Years"].map((label) => (
        <button
            key={label}
            className="px-6 py-3 text-lg font-medium text-black rounded-xl 
                    border border-gray-300 hover:bg-gray-100 transition">
            {label}
        </button>
        ))}

        <button
        className="px-8 py-3 text-xl font-semibold text-white rounded-xl 
                    bg-black hover:bg-gray-800 transition"
        >
        Search Stocks
        </button>
      </div>
    </div>
    </div>
  );
}
