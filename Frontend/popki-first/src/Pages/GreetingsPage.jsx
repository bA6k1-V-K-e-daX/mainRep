import About from "../Components/About";
import FAQs from "../Components/Faqs";
import Greeting from "../Components/Greeting";
import Rights from "../Components/Rights";
import TryPeeky from "../Components/TryPeeky";
import Yolo from "../Components/Yolo";

export default function GreetingsPage() {
  return (
    <div className='relative z-10'>
      <div className='flex flex-col min-h-screen'>
        <Greeting />
      </div>
      <About />
      <Yolo />
      <FAQs />
      <TryPeeky />
      <Rights />
    </div>
  );
}
