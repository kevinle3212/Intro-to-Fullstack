'use client';
import { useRouter } from 'next/navigation';

const Body = () => {
  const router = useRouter();

  return (
    <div className="flex flex-1 flex-col bg-white items-center">
        <p className="mt-18 text-[45px] text-black">
            OSC Finance
        </p>
        <p className="mt-5 text-[20px] text-black">
            Track Current Stock Prices For All Major Stocks
        </p>

        <button 
            onClick={() => router.push('')} 
            className="h-15 w-80 rounded-md mt-5 bg-[#444444] text-white text-[18px] hover:bg-[#343232]">
                Search Stocks Now
        </button>

        <div className="pl-5 pr-5 mt-10 border w-22 h-14 text-gray-500 text-center text-[18px]">
            S&P 500
        </div>

        <div className="flex flex-col mb-20 mt-2 pt-10 border rounded-md w-270 h-95 text-gray-500 text-center
                        items-center"> 
            Tagline
            <p className="mt-8 text-[42px] text-black font-bold">
                $99
            </p>
            <div className="h-20 w-50 mt-8 text-black text-left pl-5">
                Feature text goes here Feature text goes here Feature text goes here and more
            </div>
        <button 
            onClick={() => router.push('')} 
            className="h-10 w-22 rounded-md mt-8 bg-[#444444] text-white text-[18px] hover:bg-[#343232]">
                Button
        </button>
        </div>
    </div>
  );
};

export default Body;
