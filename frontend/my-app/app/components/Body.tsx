"use client";
import { useRouter } from "next/navigation";

export default function Body() {
  const router = useRouter();

  return (
    <div className="flex flex-col h-screen bg-white font-sans">
      {/* Top Section */}
      <div className="flex flex-1 p-10 gap-8">

        {/* Image Box */}
        <div className="rounded-lg overflow-hidden shadow-md border border-gray-300 w-[550px] h-[500px] bg-gray-200">
          <img
            src="stocks.gif"
            alt="Stocks Animation"
            className="w-full h-full object-cover opacity-90"
          />
        </div>

        {/* Stock List */}
        <div className="flex flex-col flex-1 bg-gray-100 border border-gray-300 rounded-lg shadow-sm h-[500px]">
          <p className="text-3xl font-bold text-gray-800 py-4 px-6 border-b border-gray-300">
            Top Stocks
          </p>

          <div className="flex flex-col overflow-y-auto divide-y divide-gray-300">
            {[1, 2, 3, 4].map((item) => (
              <div
                key={item}
                className="h-[120px] flex justify-between items-center px-10 hover:bg-gray-200 transition"
              >
                <p className="text-xl text-gray-700 font-medium">Stock</p>
                <img
                  src="stocks.gif"
                  alt="Stocks Animation"
                  className="w-40 h-16 opacity-90"
                />
                <p className="text-xl text-gray-700 font-medium">Value</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Buttons */}
      <div className="flex w-full h-[100px] items-center justify-center bg-gray-100 border-t border-gray-300">
        <div className="flex gap-4">
          {["Day", "Week", "Month", "Year", "5 Years"].map((label) => (
            <button
              key={label}
              className="px-6 py-3 text-lg font-medium text-black rounded-md 
                         bg-gray-300 border border-gray-400 hover:bg-gray-400 transition"
            >
              {label}
            </button>
          ))}

          <button
            className="px-8 py-3 text-xl font-semibold text-white rounded-md 
                       bg-gray-800 hover:bg-gray-700 transition"
          >
            Search Stocks
          </button>
        </div>
      </div>
    </div>
  );
}
