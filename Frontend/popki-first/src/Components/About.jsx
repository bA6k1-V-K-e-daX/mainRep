export default function About() {
  return (
    <div className='flex min-h-screen flex-col items-center gap-10 py-8 lg:flex-row lg:items-center lg:justify-between lg:gap-12 lg:py-12'>
      <div className='relative flex h-104 w-full lg:h-120 lg:max-w-3xl'>
        {/* Rectangle 10 (верхний левый) */}
        <div
          className='absolute z-10 h-auto w-56 overflow-hidden rounded-2xl shadow-lg transition-all duration-300 hover:-translate-x-4 hover:-translate-y-4 md:w-64 lg:w-72 xl:w-80'
          style={{
            top: "50%",
            left: "45%",
            transform: "translate(-70%, -80%) rotate(-15deg)",
          }}
        >
          <img
            src='Rectangle_10.png'
            alt='Pet 1'
            className='w-full h-full object-cover'
          />
        </div>

        {/* Rectangle 12 (центр) */}
        <div
          className='absolute z-30 h-auto w-56 overflow-hidden rounded-2xl shadow-2xl transition-all duration-300 hover:-translate-y-4 md:w-64 lg:w-72 xl:w-80'
          style={{
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        >
          <img
            src='Rectangle_12.png'
            alt='Pet 2'
            className='w-full h-full object-cover'
          />
        </div>

        {/* Rectangle 11 (нижний правый) */}
        <div
          className='absolute z-20 h-auto w-56 overflow-hidden rounded-2xl shadow-lg transition-all duration-300 hover:translate-x-4 hover:-translate-y-4 md:w-64 lg:w-72 xl:w-80'
          style={{
            top: "50%",
            left: "55%",
            transform: "translate(-30%, -80%) rotate(15deg)",
          }}
        >
          <img
            src='Rectangle_11.png'
            alt='Pet 3'
            className='w-full h-full object-cover'
          />
        </div>
      </div>
      <div className='w-full lg:max-w-xl'>
        <h3 className='font-semibold text-center text-2xl leading-tight md:text-4xl lg:text-4xl lg:text-start'>
          Один сервис — множество сценариев
        </h3>

        <ul
          className='mt-6 list-outside list-disc space-y-2 pl-5 text-base leading-tight md:text-lg'
          style={{ fontWeight: 300 }}
        >
          <li>E-commerce: Автоматические теги и категории.</li>
          <li>Недвижимость: Распознавание типов помещений.</li>
          <li>Безопасность: Детекция нежелательных объектов.</li>
          <li>Один API для любых задач.</li>
        </ul>
      </div>
    </div>
  );
}
