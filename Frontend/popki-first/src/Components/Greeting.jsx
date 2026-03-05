import Button from "./Button";
import { BsArrowRight } from "react-icons/bs";

export default function Greeting() {
  return (
    <div className='flex justify-center flex-1 items-center'>
      <div className='flex flex-row justify-between w-398 h-86'>
        <div className='flex w-165.75 items-start justify-start'>
          <h4 className=''>Peeky - сервис для классификации фото и видео</h4>
        </div>
        <div className='flex flex-col w-126.75 items-start justify-end'>
          <p className='text-[22px] font-normal mb-5.25'>
            Мгновенная детекция, классификация и разметка объектов для вашего
            бизнеса. Загружаете файл — получаете JSON с результатами.
          </p>
          <Button
            title='Подробнее'
            icon={<BsArrowRight className='w-7.5 h-6' />}
            className='rounded-4xl hover:bg-[#4500F9] ease-in-out duration-300'
          />
        </div>
      </div>
    </div>
  );
}
