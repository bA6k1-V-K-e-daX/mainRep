import Button from "./Button";
import { BsArrowRight } from "react-icons/bs";

export default function Greeting() {
  return (
    <div className='flex justify-center flex-1 items-center'>
      <div className='flex flex-row justify-between w-398 h-86'>
        <div className='relative flex w-165.75 flex-col items-start justify-start'>
          <h4 className=''>Peeky - сервис для классификации фото и видео</h4>
          <img
            src='AIM-3D-IRSDSCNT-V1-12.png'
            alt=''
            className='absolute -bottom-20 right-0 object-contain'
          />
        </div>
        <div className='relative w-126.75 h-full'>
          <img
            src='children-and-dog.png'
            alt='children-and-dog'
            className='absolute top-0 left-0 rounded-lg shadow-lg object-cover'
          />
          <img
            src='children-and-dog-segment.png'
            alt='children-and-dog-segment'
            className='absolute bottom-0 right-0 rounded-lg shadow-lg object-cover'
          />
        </div>
      </div>
    </div>
  );
}
