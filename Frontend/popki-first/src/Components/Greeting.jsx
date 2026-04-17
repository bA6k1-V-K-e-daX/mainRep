import Button from "./Button";
import { BsArrowRight } from "react-icons/bs";

export default function Greeting() {
  return (
    <div className='flex flex-1 items-center py-8 lg:py-12'>
      <div className='flex w-full flex-col justify-between gap-8 lg:min-h-136 lg:flex-row lg:gap-10'>
        <div className='relative flex w-full flex-col items-start justify-start lg:w-1/2'>
          <h4 className='text-4xl leading-tight md:text-5xl lg:text-6xl'>
            Peeky - сервис для классификации фото и видео
          </h4>
          <img
            src='AIM-3D-IRSDSCNT-V1-12.png'
            alt=''
            className='absolute -bottom-10 right-0 w-2/3 object-contain md:-bottom-12 lg:-bottom-16'
          />
        </div>
        <div className='relative h-80 w-full md:h-96 lg:h-full lg:w-1/2'>
          <img
            src='children-and-dog.png'
            alt='children-and-dog'
            className='absolute left-0 top-0 h-[75%] w-[72%] rounded-lg object-cover shadow-lg md:w-[68%]'
          />
          <img
            src='children-and-dog-segment.png'
            alt='children-and-dog-segment'
            className='absolute bottom-0 right-0 h-[75%] w-[72%] rounded-lg object-cover shadow-lg md:w-[68%]'
          />
        </div>
      </div>
    </div>
  );
}
