export default function Button(props) {
  const { title, className, icon } = props;

  return (
    <button
      className={` flex items-center justify-center gap-2 px-3.75 py-1 text-white border border-[#4500F9] h-8 transition-colors duration-300 ease-in-out ${className || ""}`}
    >
      {title}
      {icon}
    </button>
  );
}
