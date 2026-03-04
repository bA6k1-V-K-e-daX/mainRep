export default function About() {
  return (
    <div className='flex justify-between items-center min-h-screen'>
      <div>
        <img src='' alt='' />
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
