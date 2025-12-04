export default function SearchPage() {
  return (
    <main className="flex flex-col bg-white items-center justify-center flex-grow py-10">
  <p className="text-sm text-gray-500">OSC Stock Search</p>
  <h1 className="text-4xl text-black font-bold mt-2 mb-6">Search Any Stock Here</h1>
  
  <input
    type="text"
    placeholder="Enter stock ticker..."
    className=" bg-gray-300 text-black border border-gray-700 w-2/3 max-w-xl h-20 text-xl text-center p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  />

  <div className="mt-4 flex gap-4">
    <button className="bg-gray-800 text-white px-5 py-2 rounded-md hover:bg-gray-700">
      Search
    </button>
    <button className="bg-gray-300 text-black border border-gray-400 px-5 py-2 rounded-md hover:bg-gray-400">
      Reset
    </button>
  </div>

  <div className="mt-10 w-3/4 max-w-3xl h-48 bg-gray-200 flex items-center justify-center rounded-md">
    <span className="text-gray-500">[ Stock Chart Will Go Here ]</span>
  </div>

  <div className="mt-10 w-3/4 max-w-3xl bg-gray-100 p-6 rounded-lg shadow-sm">
  <h2 className="text-xl font-semibold mb-4 text-gray-700">Stock Information</h2>

  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-gray-800">
    <div className="flex flex-col">
      <span className="font-medium text-gray-500">Open</span>
      <span className="text-lg font-semibold">—</span>
    </div>
    <div className="flex flex-col">
      <span className="font-medium text-gray-500">High</span>
      <span className="text-lg font-semibold">—</span>
    </div>
    <div className="flex flex-col">
      <span className="font-medium text-gray-500">Low</span>
      <span className="text-lg font-semibold">—</span>
    </div>
    <div className="flex flex-col">
      <span className="font-medium text-gray-500">Close</span>
      <span className="text-lg font-semibold">—</span>
    </div>
    <div className="flex flex-col">
      <span className="font-medium text-gray-500">Volume</span>
      <span className="text-lg font-semibold">—</span>
    </div>
  </div>
</div>
</main>

  );
}
