# Проект "Анализатор погоды"
Ссылка на сайт проекта: [pogoda.silaeder.space](https://pogoda.silaeder.space)


Для локального запуска проекта:
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/mishashi/pogoda.git
   cd pogoda
2. Переименуйте .env.example в .env
   ```bash
   cp .env.example .env
4. Укажите в .env пароли
   
     FLASK_KEY — секретный ключ для Flask
   
     ADMIN_KEY — инвайт-код для регистрации администратора

     EMAIL — почта для отправки уведомлений (опциональнo)

     EMAIL_KEY — пароль приложения для почты gmail (опциональнo, как создать - см. https://support.google.com/mail/answer/185833?hl=ru)
5. Запустите docker
 ```bash
  sudo docker compose up --build -d



