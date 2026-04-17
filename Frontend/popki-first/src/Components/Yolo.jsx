export default function Yolo() {
  return (
    <div className='mb-16 flex flex-col items-center gap-8 lg:mb-20 lg:flex-row lg:justify-between lg:gap-10'>
      <div className='w-full hyphens-auto lg:w-1/2'>
        <h1 className='font-semibold text-3xl leading-tight md:text-4xl lg:text-5xl'>
          Интеллектуальная сегментация SAM 3
        </h1>
        <p className='mt-6 text-base leading-relaxed md:text-lg'>
          Без компромиссов между скоростью и качеством. Мы используем потоковую
          модель SAM 3 для анализа видео за один проход. Безупречная точность
          выделения, понимание пространственно-временного контекста и
          минимальный пинг. Идеально для работы с потоковым видео в реальном
          времени.
        </p>
      </div>
      <div className='h-auto w-full lg:w-1/2'>
        <img src='Rectangle_13.png' alt='' className='w-full rounded-2xl object-cover' />
      </div>
    </div>
  );
}
