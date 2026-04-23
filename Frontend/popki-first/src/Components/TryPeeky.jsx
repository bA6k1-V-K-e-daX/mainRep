import { MdOutlineArrowOutward } from "react-icons/md";
import { Link } from "react-router-dom";

export default function TryPeeky() {
  return (
    <div className='mx-auto mt-16 mb-16 flex w-full max-w-screen-2xl flex-col justify-between gap-8 lg:mt-24 lg:mb-20 lg:flex-row lg:gap-12'>
      <div className=''>
        <img
          src='big_logo.png'
          alt=''
          className='w-full max-w-xl object-contain'
        />
      </div>
      <div className='flex w-full flex-col min-h-40 justify-between lg:max-w-2xl'>
        <div>
          <h3 className='text-2xl text-center font-semibold leading-tight md:text-4xl lg:text-5xl'>
            Попробуйте Peeky в деле
          </h3>
        </div>
        <div>
          <Link to='/registr'>
            <button className='group relative flex w-full items-center gap-1 justify-between overflow-hidden text-2xl font-light text-white focus:outline-none md:text-3xl lg:text-4xl'>
              <span>Давайте начнём</span>
              <MdOutlineArrowOutward className='h-8 w-8 transform transition-transform duration-300 group-hover:-translate-y-2 group-hover:translate-x-2 md:h-10 md:w-10' />
              <div className='absolute bottom-0 left-0 w-full h-0.5 bg-blue-600'></div>
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
