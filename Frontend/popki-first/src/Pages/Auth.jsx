import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Button from "../Components/Button";
import { login } from "../api/api";

export default function Auth() {
  const navigate = useNavigate();
  const [loginValue, setLoginValue] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await login({ login: loginValue, password });
      localStorage.setItem("auth_token", response.token);
      navigate("/workspace");
    } catch (err) {
      setError(err.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className='relative mx-auto flex h-[calc(100vh-200px)] w-full max-w-6xl items-center justify-center overflow-hidden py-4 md:py-8'>
      <div className='grid w-full grid-cols-1 items-center gap-8 lg:grid-cols-[360px_1fr] lg:gap-20'>
        <figure className='mx-auto w-full max-w-[360px]'>
          <img
            src='/robot-performing-ordinary-human-job.png'
            alt='Робот рисует картину'
            className='h-[420px] w-full rounded-[18px] object-cover shadow-[0_0_30px_rgba(69,0,249,0.35)]'
          />
        </figure>

        <div className='mx-auto w-full max-w-xl'>
          <h1 className='mb-8 text-4xl font-semibold leading-tight text-[var(--text-primary)] md:text-5xl'>
            Авторизация
          </h1>

          <form className='space-y-8' onSubmit={handleSubmit}>
            <div className='space-y-6'>
              <label htmlFor='auth-login' className='sr-only'>
                Логин или почта
              </label>
              <input
                id='auth-login'
                type='text'
                placeholder='Логин/Почта'
                value={loginValue}
                onChange={(e) => setLoginValue(e.target.value)}
                required
                className='w-full border-b border-[var(--border-brand)] bg-transparent pb-2 text-base text-[var(--text-primary)] placeholder:text-[var(--text-label)] focus:outline-none focus:ring-0'
              />

              <label htmlFor='auth-password' className='sr-only'>
                Пароль
              </label>
              <input
                id='auth-password'
                type='password'
                placeholder='Пароль'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className='w-full border-b border-[var(--border-brand)] bg-transparent pb-2 text-base text-[var(--text-primary)] placeholder:text-[var(--text-label)] focus:outline-none focus:ring-0'
              />
            </div>

            {error && <p className="text-sm text-[var(--text-error)]">{error}</p>}

            <div className='flex flex-wrap items-center justify-between gap-4'>
              <p className='text-sm text-[var(--text-label)]'>
                Нет аккаунта?{" "}
                <Link
                  to='/registr'
                  className='text-[var(--bg-brand)] transition-colors duration-300 hover:text-[var(--bg-brand-hover)]'
                >
                  Регистрация
                </Link>
              </p>

              <Button
                title={loading ? "Входим..." : "Войти"}
                disabled={loading}
                className='h-8 min-w-[110px] rounded-lg border-0 bg-[var(--bg-brand)] text-sm hover:bg-[var(--bg-brand-hover)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--bg-brand-hover)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-primary)]'
              />
            </div>
          </form>
        </div>
      </div>

      <img
        src='/abstract_form.png'
        alt='Декоративная абстрактная форма'
        aria-hidden='true'
        className='pointer-events-none absolute -bottom-2 right-0 hidden w-36 opacity-95 md:block lg:w-44'
      />
    </section>
  );
}