import { Link } from "react-router-dom";
import Button from "../Components/Button";

export default function Registration() {
  return (
    <>
      <div>
        <div>
          <h1>Текст - текст</h1>
          <img src='Rectangle_11.png' alt='' />
        </div>
        <div>
          <h1>Новый аккаунт</h1>
          <form>
            <input type='text' placeholder='Логин/Почта' required />

            <input type='password' placeholder='Пароль' required />

            <div>
              <span>
                Уже есть аккаунт? - <Link to='/signin'>Авторизация</Link>
              </span>
              <Button>Создать</Button>
            </div>
          </form>
          <input type='email' />
        </div>
      </div>
    </>
  );
}
