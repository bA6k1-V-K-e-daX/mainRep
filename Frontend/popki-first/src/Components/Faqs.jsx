import { useState } from "react";

const FAQItem = ({ question, answer, number }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className='border-b border-blue-800 pb-2 mb-4 last:mb-0'>
      <button
        className='flex w-full items-center justify-between py-4 text-left text-white focus:outline-none md:py-5'
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className='flex items-center'>
          <span className='mr-3 text-lg font-thin md:mr-4 md:text-2xl'>
            {number.toString().padStart(2, "0")}
          </span>
          <span className='text-xl font-thin leading-tight md:text-2xl lg:text-3xl'>
            {question}
          </span>
        </div>
        <svg
          className={`h-6 w-6 transform transition-transform duration-300 md:h-8 md:w-8 ${isOpen ? "rotate-180" : ""}`}
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
          xmlns='http://www.w3.org/2000/svg'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth='2'
            d='M19 9l-7 7-7-7'
          ></path>
        </svg>
      </button>
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className='py-2 pl-8 text-gray-300 md:pl-12'>
          <h5>{answer}</h5>
        </div>
      </div>
    </div>
  );
};

const FAQs = () => {
  const faqsData = [
    {
      question: "С какими форматами файлов работает Peeky?",
      answer:
        "Peeky поддерживает широкий спектр форматов изображений, включая JPG, PNG, WEBP, а также видеоформаты MP4, AVI, MOV.",
    },
    {
      question: "Можно ли интегрировать сервис в мое приложение?",
      answer:
        "Да, Peeky предоставляет API для легкой интеграции в ваши веб- и мобильные приложения через Rest API. Ознакомьтесь с нашей документацией для разработчиков.",
    },
    {
      question: "Сколько времени занимает обработка?",
      answer:
        "Инференс моделей занимает миллисекунды. Вы получаете результат практически мгновенно.",
    },
    {
      question: "Безопасны ли мои данные?",
      answer:
        "Мы очень серьезно относимся к безопасности данных. Все файлы обрабатываются на защищенных серверах, а передача данных осуществляется по зашифрованным каналам.",
    },
  ];

  return (
    <div className='flex min-h-screen items-center justify-center py-8 lg:py-12'>
      <div className='w-full max-w-5xl xl:max-w-7xl'>
        {faqsData.map((faq, index) => (
          <FAQItem
            key={index}
            number={index + 1}
            question={faq.question}
            answer={faq.answer}
          />
        ))}
      </div>
    </div>
  );
};

export default FAQs;
