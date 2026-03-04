import { useState } from "react";

const FAQItem = ({ question, answer, number }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className='border-b border-blue-800 pb-4 mb-4 last:mb-0'>
      <button
        className='flex justify-between items-center w-full text-white text-left py-4 focus:outline-none'
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className='text-xl font-light'>
          <span className='text-gray-500 mr-4'>
            {number.toString().padStart(2, "0")}
          </span>
          {question}
        </span>
        <svg
          className={`w-6 h-6 transform transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
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
        <div className='py-2 pl-12 text-gray-300'>
          <p>{answer}</p>
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
    <div className='min-h-screen flex items-center justify-center'>
      <div className='w-full max-w-350'>
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
