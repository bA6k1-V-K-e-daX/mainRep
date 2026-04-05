import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";

import GreetingsPage from "./Pages/GreetingsPage";
import Auth from "./Pages/Auth";
import Registration from "./Pages/Registration";
import Header from "./Components/Header";

import glowSpots from "./Constants/DATA";

function App() {
  return (
    <>
      <Router>
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
          <Header />
          <main>
            <Routes>
              <Route path='/' element={<GreetingsPage />} />
              <Route path='/signin' element={<Auth />} />
              <Route path='/registr' element={<Registration />} />
              <Route path='*' element={<div>404: Страница не найдена</div>} />
            </Routes>
          </main>
        </div>
      </Router>
    </>
  );
}

export default App;
