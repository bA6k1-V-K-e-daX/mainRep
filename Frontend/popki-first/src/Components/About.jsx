export default function About() {
  return (
    <div className='flex justify-between items-center min-h-screen'>
      <div className='relative flex max-w-163 w-full h-100'>
        {/* Rectangle 10 (верхний левый) */}
        <div
          className='absolute w-96 h-auto rounded-2xl overflow-hidden shadow-lg z-10 transition-all duration-300 hover:-translate-y-4 hover:-translate-x-4'
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
          className='absolute w-96 h-auto rounded-2xl overflow-hidden shadow-2xl z-30 transition-all duration-300 hover:-translate-y-4'
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
          className='absolute w-96 h-auto rounded-2xl overflow-hidden shadow-lg z-20 transition-all duration-300 hover:-translate-y-4 hover:translate-x-4'
          style={{
            top: "15%",
            left: "55%",
            transform: "translate(-30%, -20%) rotate(15deg)",
          }}
        >
          <img
            src='Rectangle_11.png'
            alt='Pet 3'
            className='w-full h-full object-cover'
          />
        </div>
      </div>
      <div className='w-134.75'>
        <h1>Один сервис — множество сценариев</h1>

        <p className='mt-4.5 '>
          От сортировки товаров для маркетплейсов до модерации контента в
          соцсетях
          <ul
            className='mt-4.5 list-disc list-inside'
            style={{ fontWeight: 300 }}
          >
            <li>E-commerce: Автоматические теги и категории.</li>
            <li>Недвижимость: Распознавание типов помещений.</li>
            <li>Безопасность: Детекция нежелательных объектов.</li>
            <li>Один API для любых задач.</li>
          </ul>
        </p>
      </div>
    </div>
  );
}
