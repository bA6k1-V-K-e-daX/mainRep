import { Link } from "react-router-dom";
import Button from "../Components/Button";

export default function Auth() {
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
            Авторизация
          </h1>

          <form className='space-y-8'>
            <div className='space-y-6'>
              <label htmlFor='auth-login' className='sr-only'>
                Логин или почта
              </label>
              <input
                id='auth-login'
                type='text'
                placeholder='Логин/Почта'
                required
                className='w-full border-b border-[#4500F9] bg-transparent pb-2 text-base text-white placeholder:text-[#8A84B5] focus:outline-none focus:ring-0'
              />

              <label htmlFor='auth-password' className='sr-only'>
                Пароль
              </label>
              <input
                id='auth-password'
                type='password'
                placeholder='Пароль'
                required
                className='w-full border-b border-[#4500F9] bg-transparent pb-2 text-base text-white placeholder:text-[#8A84B5] focus:outline-none focus:ring-0'
              />
            </div>

            <div className='flex flex-wrap items-center justify-between gap-4'>
              <p className='text-sm text-[#8A84B5]'>
                Нет аккаунта?{" "}
                <Link
                  to='/registr'
                  className='text-[#6B5CFF] transition-colors duration-300 hover:text-[#9C92FF]'
                >
                  Регистрация
                </Link>
              </p>

              <Button
                title='Войти'
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
