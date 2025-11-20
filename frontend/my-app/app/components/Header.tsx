'use client';
import { useRouter } from 'next/navigation';

const Header = () => {
  const router = useRouter();

  return (
        <header className="flex justify-between items-center w-full 
                          h-20 bg-gray-300 border-b border-gray-500 px-8">
            <h1 className="text-[26px] font-bold text-black">
                AI Stock Analysis
            </h1>
          <nav className="flex gap-15 pr-24">
            <button onClick={() => router.push('/')} 
                className="text-[18px] text-black font-medium hover:underline">
                Home
            </button>

            <button onClick={() => router.push('/search')} 
                className="text-[18px] text-black font-medium hover:underline">
                Stock Search
            </button>

            <button 
            onClick={() => router.push('/about')} 
            className="text-[18px] text-black font-medium hover:underline">
            About
            </button>
          </nav>
        </header>
  );
};

export default Header;