import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import "./App.css";

import { MediaProvider } from "./context/MediaProvider";
import Workspace from "./Pages/Workspace";
import GreetingsPage from "./Pages/GreetingsPage";
import Auth from "./Pages/Auth";
import Registration from "./Pages/Registration";
import Header from "./Components/Header";

import glowSpots from "./Constants/DATA";

// 1. Создаем внутренний компонент, который находится ВНУТРИ <Router>
// Теперь здесь можно безопасно использовать useLocation()
function AppContent() {
  const location = useLocation();

  // Массив путей, где Header должен быть скрыт
  const hideHeaderRoutes = ["/workspace"];
  const showHeader = !hideHeaderRoutes.includes(location.pathname);

  return (
    <div className='relative min-h-screen flex flex-col'>
      {/* Блок со свечениями (находится на заднем фоне) */}
      <div className='absolute inset-0 pointer-events-none z-0 overflow-hidden'>
        {glowSpots.map((spot) => (
          <div
            key={spot.id}
            className={`absolute rounded-full blur-[120px] mix-blend-screen ${spot.color} ${spot.opacity}`}
            style={{
              top: spot.top,
              bottom: spot.bottom,
              left: spot.left,
              right: spot.right,
              width: `clamp(${spot.minSize}, 40vw, ${spot.maxSize})`,
              height: `clamp(${spot.minSize}, 40vw, ${spot.maxSize})`,
            }}
          />
        ))}
      </div>

      {/* Показываем Header только если мы не на странице /workspace */}
      {showHeader && <Header />}

      {/* Основной контент */}
      <main className='flex-1 flex flex-col relative z-10'>
        <Routes>
          <Route path='/' element={<GreetingsPage />} />
          <Route path='/signin' element={<Auth />} />
          <Route path='/registr' element={<Registration />} />
          <Route path='/workspace' element={<Workspace />} />
          <Route path='*' element={<div>404: Страница не найдена</div>} />
        </Routes>
      </main>
    </div>
  );
}

// 2. Главный компонент App просто оборачивает все в Провайдеры
function App() {
  return (
    <MediaProvider>
      <Router>
        <AppContent />
      </Router>
    </MediaProvider>
  );
}

export default App;
