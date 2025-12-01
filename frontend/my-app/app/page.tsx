import Header from "./components/Header";
import Body from "./components/Body";
import Footer from "./components/Footer";

export default function Page() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header/>
      <Body/>
      <Footer/>
    </div>
  );
}
