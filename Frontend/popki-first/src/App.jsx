import "./App.css";
import About from "./Components/About";
import Greeting from "./Components/Greeting";
import Header from "./Components/Header";

function App() {
  return (
    <>
      <div className='flex flex-col min-h-screen'>
        <Header />
        <Greeting />
      </div>
      <About />
    </>
  );
}

export default App;
