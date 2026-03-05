import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import "./App.css";

import GreetingsPage from "./Pages/GreetingsPage";
import Auth from "./Pages/Auth";
import Registration from "./Pages/Registration";

function App() {
  return (
    <Router>
      <main>
        <Routes>
          <Route path='/' element={<GreetingsPage />} />
          <Route path='/signin' element={<Auth />} />
          <Route path='/registr' element={<Registration />} />
          <Route path='*' element={<div>404: Страница не найдена</div>} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
