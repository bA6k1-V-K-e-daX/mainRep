import About from "../Components/About";
import FAQs from "../Components/Faqs";
import Greeting from "../Components/Greeting";
import Header from "../Components/Header";
import Rights from "../Components/Rights";
import TryPeeky from "../Components/TryPeeky";
import Yolo from "../Components/Yolo";

// --- НАСТРОЙКИ СВЕЧЕНИЙ ---
// Здесь ты можешь добавлять, удалять и настраивать пятна
const glowSpots = [
  {
    id: 1,
    top: "5%", // Позиция сверху (в % от всей высоты страницы)
    left: "-10%", // Позиция слева (отрицательная, чтобы часть уходила за край)
    color: "bg-[#4500F9]", // Цвет Tailwind
    opacity: "opacity-40", // Прозрачность
    minSize: "250px", // Минимальный размер (на мобилках)
    maxSize: "700px", // Максимальный размер (на больших экранах)
  },
  {
    id: 2,
    top: "40%",
    right: "-5%",
    color: "bg-[#4500F9]",
    opacity: "opacity-30",
    minSize: "200px",
    maxSize: "600px",
  },
  {
    id: 3,
    bottom: "10%",
    left: "10%",
    color: "bg-[#4500F9]",
    opacity: "opacity-20",
    minSize: "300px",
    maxSize: "800px",
  },
];

export default function GreetingsPage() {
  return (
    // 1. Главная обертка.
    // relative - чтобы пятна позиционировались относительно всей страницы.
    // overflow-x-hidden - ОБЯЗАТЕЛЬНО, чтобы блюр за краями экрана не создавал горизонтальный скролл.
    // bg-[#0a0514] - темный фон страницы (замени на свой, если нужен другой)
    <div className='relative min-h-screen'>
      {/* 2. Блок со свечениями (находится на заднем фоне) */}
      <div className='absolute inset-0 pointer-events-none z-0'>
        {glowSpots.map((spot) => (
          <div
            key={spot.id}
            className={`absolute rounded-full blur-[120px] mix-blend-screen ${spot.color} ${spot.opacity}`}
            style={{
              top: spot.top,
              bottom: spot.bottom,
              left: spot.left,
              right: spot.right,
              // Магия адаптивности: clamp(МИН_РАЗМЕР, ЖЕЛАЕМЫЙ_РАЗМЕР_В_%, МАКС_РАЗМЕР)
              width: `clamp(${spot.minSize}, 40vw, ${spot.maxSize})`,
              height: `clamp(${spot.minSize}, 40vw, ${spot.maxSize})`,
            }}
          />
        ))}
      </div>

      {/* 3. Основной контент (должен быть поверх свечений, поэтому relative z-10) */}
      <div className='relative z-10'>
        <div className='flex flex-col min-h-screen'>
          <Header />
          <Greeting />
        </div>
        <About />
        <Yolo />
        <FAQs />
        <TryPeeky />
        <Rights />
      </div>
    </div>
  );
}
