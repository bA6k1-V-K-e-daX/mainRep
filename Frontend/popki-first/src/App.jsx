import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import { useEffect, useState } from "react";
import "./App.css";

import { MediaProvider } from "./context/MediaProvider";
import { ThemeProvider } from "./context/ThemeContext";
import Workspace from "./Pages/Workspace";
import GreetingsPage from "./Pages/GreetingsPage";
import Auth from "./Pages/Auth";
import Registration from "./Pages/Registration";
import Header from "./Components/Header";
import { getHelloMessage } from "./api/api";

import glowSpots from "./Constants/DATA";

// 1. Создаем внутренний компонент, который находится ВНУТРИ <Router>
// Теперь здесь можно безопасно использовать useLocation()
function AppContent() {
  const location = useLocation();
  const [backendMessage, setBackendMessage] = useState("");
  const [isLoadingMessage, setIsLoadingMessage] = useState(true);
  const [messageError, setMessageError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadHelloMessage = async () => {
      setIsLoadingMessage(true);
      setMessageError("");

      try {
        const data = await getHelloMessage();
        if (!isMounted) return;
        setBackendMessage(data?.message ?? "");
      } catch (error) {
        if (!isMounted) return;
        setMessageError(
          error instanceof Error
            ? error.message
            : "Не удалось получить сообщение с сервера",
        );
      } finally {
        if (isMounted) {
          setIsLoadingMessage(false);
        }
      }
    };

    loadHelloMessage();

    return () => {
      isMounted = false;
    };
  }, []);

  // Массив путей, где Header должен быть скрыт
  const hideHeaderRoutes = ["/workspace"];
  const showHeader = !hideHeaderRoutes.includes(location.pathname);

  return (
    <div className='relative min-h-screen w-full flex flex-col'>
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
      <main className='relative z-10 flex flex-1 flex-col'>
        <div
          className={`w-full flex-1 ${
            showHeader
              ? "mx-auto w-full max-w-screen-2xl px-4 py-4 md:px-6 md:py-6 lg:px-8 lg:py-8 xl:px-10 2xl:px-12"
              : ""
          }`}
        >
          {isLoadingMessage && console.log("Загрузка сообщения с сервера...")}
          {!isLoadingMessage &&
            messageError &&
            console.log(`Ошибка: ${messageError}`)}
          {!isLoadingMessage &&
            !messageError &&
            console.log(`Сообщение от бэкенда: ${backendMessage}`)}

          <Routes>
            <Route path='/' element={<GreetingsPage />} />
            <Route path='/signin' element={<Auth />} />
            <Route path='/registr' element={<Registration />} />
            <Route path='/workspace' element={<Workspace />} />
            <Route path='*' element={<div>404: Страница не найдена</div>} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

// 2. Главный компонент App просто оборачивает все в Провайдеры
function App() {
  return (
    <ThemeProvider>
      <MediaProvider>
        <Router>
          <AppContent />
        </Router>
      </MediaProvider>
    </ThemeProvider>
  );
}

export default App;
