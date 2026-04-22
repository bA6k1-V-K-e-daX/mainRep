export default function Yolo() {
  return (
    <div className='flex flex-col items-center justify-between gap-8 mb-10 min-h-[550px] lg:mb-20 lg:flex-row lg:justify-between lg:gap-10'>
      <div className=' w-full hyphens-auto lg:w-5/12'>
        <h3 className='font-semibold text-2xl text-center mb-20 leading-tight md:text-3xl md:text-start lg:text-4xl lg:mb-0'>
          Интеллектуальная сегментация SAM 3
        </h3>
        <p className='mt-6 text-base leading-relaxed font-normal hidden md:text-lg md:block'>
          Без компромиссов между скоростью и качеством. Мы используем потоковую
          модель SAM 3 для анализа видео за один проход. Безупречная точность
          выделения, понимание пространственно-временного контекста и
          минимальный пинг. Идеально для работы с потоковым видео в реальном
          времени.
        </p>
        <p className='mt-6 text-base leading-relaxed md:text-lg md:hidden'>
          Анализ видео в реальном времени с SAM 3. Обработка за один проход:
          безупречная точность, понимание контекста и минимальная задержка.
          Никаких компромиссов между скоростью и качеством.
        </p>
      </div>
      <div className='h-auto w-4/5 mx-auto lg:w-1/3'>
        <img
          src='Rectangle_13.png'
          alt=''
          className='w-full rounded-2xl object-cover'
        />
      </div>
    </div>
  );
}
