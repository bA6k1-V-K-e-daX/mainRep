import { MdOutlineArrowOutward } from "react-icons/md";
import { Link } from "react-router-dom";

export default function TryPeeky() {
  return (
    <div className='flex justify-between mt-30 mb-20 max-w-350 mx-auto'>
      <div className=''>
        <img src='big_logo.png' alt='' />
      </div>
      <div className='flex flex-col max-w-162.5 justify-between'>
        <div>
          <h1>Попробуйте Peeky в деле</h1>
          <p className='mt-7.5'>
            Зарегистрируйтесь и загрузите первый файл. Оцените точность
            распознавания и скорость работы Peeky прямо сейчас.
          </p>
        </div>
        <div>
          <Link to='/registr'>
            <button className='relative flex items-center justify-between w-full max-w-3xl text-white text-[32px] font-light overflow-hidden group focus:outline-none'>
              <span>Давайте начнём</span>
              <MdOutlineArrowOutward className='w-10 h-10 transform transition-transform duration-300 group-hover:-translate-y-2 group-hover:translate-x-2' />
              <div className='absolute bottom-0 left-0 w-full h-0.5 bg-blue-600'></div>
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
