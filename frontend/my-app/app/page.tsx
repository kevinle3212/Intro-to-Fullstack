import Header from "./components/Header";
import Body from "./components/Body";

export default function Page() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header/>
      <Body/>
    </div>
  );
}
