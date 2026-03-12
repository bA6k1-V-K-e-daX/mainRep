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

export default glowSpots;
