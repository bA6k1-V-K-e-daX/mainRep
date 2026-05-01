import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Button from "../Components/Button";
import { register } from "../api/api";

export default function Registration() {
  const navigate = useNavigate();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    if (!login.trim()) {
      setError("Введите логин");
      return false;
    }
    if (password.length < 6) {
      setError("Пароль должен быть не менее 6 символов");
      return false;
    }
    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      await register({ login, password });
      navigate("/signin");
    } catch (err) {
      setError(err.message || "Ошибка регистрации");
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
          <h1 className='mb-8 text-4xl font-semibold leading-tight text-white md:text-5xl'>
            Новый аккаунт
          </h1>

          <form className='space-y-8' onSubmit={handleSubmit}>
            <div className='space-y-6'>
              <label htmlFor='registration-login' className='sr-only'>
                Логин или почта
              </label>
              <input
                id='registration-login'
                type='text'
                placeholder='Логин/Почта'
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                required
                className='w-full border-b border-[#4500F9] bg-transparent pb-2 text-base text-white placeholder:text-[#8A84B5] focus:outline-none focus:ring-0'
              />

              <label htmlFor='registration-password' className='sr-only'>
                Пароль
              </label>
              <input
                id='registration-password'
                type='password'
                placeholder='Пароль'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className='w-full border-b border-[#4500F9] bg-transparent pb-2 text-base text-white placeholder:text-[#8A84B5] focus:outline-none focus:ring-0'
              />

              <label htmlFor='registration-confirm-password' className='sr-only'>
                Повторите пароль
              </label>
              <input
                id='registration-confirm-password'
                type='password'
                placeholder='Повторите пароль'
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className='w-full border-b border-[#4500F9] bg-transparent pb-2 text-base text-white placeholder:text-[#8A84B5] focus:outline-none focus:ring-0'
              />
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}

            <div className='flex flex-wrap items-center justify-between gap-4'>
              <p className='text-sm text-[#8A84B5]'>
                Уже есть аккаунт?{" "}
                <Link
                  to='/signin'
                  className='text-[#6B5CFF] transition-colors duration-300 hover:text-[#9C92FF]'
                >
                  Авторизация
                </Link>
              </p>

              <Button
                title={loading ? "Создаётся..." : "Создать"}
                disabled={loading}
                className='h-8 min-w-[110px] rounded-lg border-0 bg-[#4500F9] text-sm hover:bg-[#5A22FF] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7D66FF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#070018]'
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
