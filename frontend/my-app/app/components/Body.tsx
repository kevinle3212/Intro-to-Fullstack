'use client';
import { useRouter } from 'next/navigation';

const Body = () => {
  const router = useRouter();

  return (
    <div className="flex flex-1 flex-col h-screen bg-white">
        <div className="flex flex-1">
            <div className="img-box h-[500px] w-[550px]">
                <img src="stocks.gif" alt="Stocks Animation" className="w-full h-full object-cover">
                </img>
            </div>

            <div className="flex flex-col flex-1 text-center border-black border-[1px] h-[500px]">
                <p className="text-[45px] text-black h-[80px]">
                    Top Stocks 
                </p>
                <div className="flex flex-col text-center border-black border-[1px] h-[500px] overflow-y-auto">
                    <div className="h-[125px] justify-center items-center 
                    flex border-black border-[1px] border-l-0 text-black">
                        <p className="text-[26px]">
                            Stock
                        </p>
                        <img src="stocks.gif" alt="Stocks Animation" className="w-60 h-20 ml-20 mr-20 hover:opacity-80 duration-200">
                        </img>
                        <p className="text-[26px]">
                            Value
                        </p>
                    </div>

                    <div className="h-[125px] justify-center items-center 
                    flex border-black border-[1px] border-l-0 text-black">
                        <p className="text-[26px]">
                            Stock
                        </p>
                        <img src="stocks.gif" alt="Stocks Animation" className="w-60 h-20 ml-20 mr-20 hover:opacity-80 duration-200">
                        </img>
                        <p className="text-[26px]">
                            Value
                        </p>
                    </div>

                    <div className="h-[125px] justify-center items-center 
                    flex border-black border-[1px] border-l-0 text-black">
                        <p className="text-[26px]">
                            Stock
                        </p>
                        <img src="stocks.gif" alt="Stocks Animation" className="w-60 h-20 ml-20 mr-20 hover:opacity-80 duration-200">
                        </img>
                        <p className="text-[26px]">
                            Value
                        </p>
                    </div>

                    <div className="h-[125px] justify-center items-center 
                    flex border-black border-[1px] border-l-0 text-black">
                        <p className="text-[26px]">
                            Stock
                        </p>
                        <img src="stocks.gif" alt="Stocks Animation" className="w-60 h-20 ml-20 mr-20 hover:opacity-80 duration-200">
                        </img>
                        <p className="text-[26px]">
                            Value
                        </p>
                    </div>

                </div> 
            </div>
        </div>
        <div className="flex h-[100px] w-[1300px] justify-center items-center">
            <button className="h-full w-[190px] text-black text-[20px]
            hover:bg-gray-200 border-r">
                Day
            </button>
            <button className="h-full w-[190px] text-black text-[20px]
            hover:bg-gray-200 border-r">
                Week
            </button>
            <button className="h-full w-[190px] text-black text-[20px]
            hover:bg-gray-200 border-r">
                Month
            </button>
            <button className="h-full w-[190px] text-black text-[20px]
            hover:bg-gray-200 border-r">
                Year
            </button>
            <button className="h-full w-[190px] text-black text-[20px]
            hover:bg-gray-200 border-r">
                5 Years
            </button>
            <div className="flex h-full w-full justify-center items-center text-white text-[32px] bg-black hover:bg-gray-800">
                    Search Stocks
            </div>
        </div>
    </div>
  );
};

export default Body;
