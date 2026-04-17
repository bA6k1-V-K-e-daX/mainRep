import Button from "./Button";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <div className='w-full'>
      <div className='mx-auto my-6 flex h-14 w-full max-w-screen-2xl items-center justify-between rounded-2xl border border-[#4500F9] px-4 py-2 md:my-8 md:px-6 lg:px-8'>
        <div className='flex items-center'>
          <Link to='/' className='flex items-center gap-2'>
            <img src='peeky-mini-logo.png' alt='' className='w-10 h-10' />
            <p className='m-0 text-white text-2xl font-extralight tracking-normal'>
              Peeky
            </p>
          </Link>
        </div>
        <div className='flex gap-3.5'>
          <Link to='/signin'>
            <Button
              title='Войти'
              className='w-20 rounded-lg hover:border-0 hover:bg-[#4500F9]'
            />
          </Link>

          <Link to='/registr'>
            <Button
              title='Начать'
              className='w-20 rounded-lg bg-[#4500F9] border-0 hover:bg-transparent hover:border'
            />
          </Link>
        </div>
      </div>
    </div>
  );
}
