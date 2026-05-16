import Button from "./Button";
import { Link } from "react-router-dom";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const isLight = theme === "light";

  return (
    <div className='w-full'>
      <div className='mx-auto my-6 flex h-14 w-[95%] max-w-screen-2xl items-center justify-between rounded-2xl border border-[var(--border-brand)] bg-[var(--bg-secondary)] px-4 py-2 md:my-8 md:px-6 md:w-50% lg:px-8 lg:w-[40%]'>
        <div className='flex items-center'>
          <Link to='/' className='flex items-center gap-2'>
            <img src='peeky-mini-logo.png' alt='' className='w-10 h-10' />
            <p className='m-0 text-[var(--text-light)] text-xl font-extralight tracking-normal lg:text-2xl'>
              Peeky
            </p>
          </Link>
        </div>
        <div className='flex items-center gap-3.5'>
          <button
            onClick={toggleTheme}
            className='flex h-9 w-9 items-center justify-center rounded-full bg-white/10 transition hover:bg-white/20'
            aria-label='Переключить тему'
          >
            {isLight ? (
              <Moon className='h-4 w-4 text-white' />
            ) : (
              <Sun className='h-4 w-4 text-white' />
            )}
          </button>
          <Link to='/signin'>
            <Button
              title='Войти'
              className='w-20 rounded-lg hover:border-0 hover:bg-[var(--bg-brand)]'
            />
          </Link>

          <Link to='/registr'>
            <Button
              title='Начать'
              className='w-20 rounded-lg bg-[var(--bg-brand)] border-0 hover:bg-transparent hover:border'
            />
          </Link>
        </div>
      </div>
    </div>
  );
}