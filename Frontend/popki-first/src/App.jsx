import "./App.css";
import About from "./Components/About";
import FAQs from "./Components/Faqs";
import Greeting from "./Components/Greeting";
import Header from "./Components/Header";
import Rights from "./Components/Rights";
import TryPeeky from "./Components/TryPeeky";
import Yolo from "./Components/Yolo";

function App() {
  return (
    <>
      <div className='flex flex-col min-h-screen'>
        <Header />
        <Greeting />
      </div>
      <About />
      <Yolo />
      <FAQs />
      <TryPeeky />
      <Rights />
    </>
  );
}

export default App;
