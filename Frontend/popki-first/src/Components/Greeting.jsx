import Button from "./Button";

export default function Greeting() {
  return (
    <div className='flex flex-1 items-start pt-[clamp(86px,13.65vw,340px)] md:pb-8 lg:pb-12'>
      <div className='flex w-full flex-col gap-8 lg:flex-row lg:gap-10 lg:justify-between'>
        <div className='relative flex justify-between min-h-[600px] w-full flex-col items-start lg:min-h-[520px] lg:w-1/2'>
          <div>
            <h4 className='max-w-[17ch] text-[2rem] text-justify font-semibold leading-normal md:text-5xl lg:max-w-none lg:text-6xl/[120%] lg: lg:text-start'>
              Peeky - сервис для классификации фото и видео
            </h4>
            <img
              src='AIM-3D-IRSDSCNT-V1-12.png'
              alt=''
              className='absolute top-50 right-0 w-[58%] max-w-xs object-contain md:bottom-4 md:w-1/2 lg:bottom-0 lg:max-w-sm'
            />
          </div>
          <div>
            <p className='flex justify-end mb-10 md:hidden'>
              Peeky — это сервис компьютерного зрения на базе нейросетей.
              Мгновенная детекция, классификация и разметка объектов для вашего
              бизнеса. Загружаете файл — получаете JSON с результатами.
            </p>
          </div>
        </div>
        <div className='relative hidden h-[520px] w-full lg:block lg:w-[40%] xl:h-[360px]'>
          <img
            src='children-and-dog.png'
            alt='children-and-dog'
            className='absolute left-0 top-0 h-[76%] w-[72%] rounded-[20px] object-cover shadow-lg xl:w-[70%]'
          />
          <img
            src='children-and-dog-segment.png'
            alt='children-and-dog-segment'
            className='absolute bottom-0 right-0 h-[76%] w-[72%] rounded-[20px] object-cover shadow-lg xl:w-[70%]'
          />
        </div>
      </div>
    </div>
  );
}
