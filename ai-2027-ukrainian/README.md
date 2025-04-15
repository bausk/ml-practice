# ШІ 2027 (Ukrainian Version)

Український переклад інтерактивної сторінки [AI 2027](https://ai-2027.com/race), яка прогнозує розвиток штучного інтелекту до 2027 року.

## Опис проекту

Цей проект — статичний веб-сайт з українським перекладом сценарію "Гонка ШІ" з оригінального сайту AI 2027. Переклад повністю зберігає оригінальний зміст, представляючи його українською мовою.

## Демо

Демо доступне за посиланням: [https://ai-2027-ukrainian.vercel.app](https://ai-2027-ukrainian.vercel.app)

## Технології

- HTML5
- CSS3
- JavaScript (vanilla)
- Vercel для деплойменту

## Локальне встановлення

1. Клонуйте репозиторій:
```bash
git clone https://github.com/yourusername/ai-2027-ukrainian.git
cd ai-2027-ukrainian
```

2. Встановіть залежності:
```bash
npm install
```

3. Запустіть локальний сервер:
```bash
npm run dev
```

4. Відкрийте браузер за адресою `http://localhost:3000`

## Структура проекту

```
ai-2027-ukrainian/
├── index.html            # Головна сторінка
├── styles.css            # Стилі
├── script.js             # JavaScript функціональність
├── 404.html              # Сторінка 404 помилки
├── robots.txt            # Інструкції для пошукових роботів
├── server.js             # Локальний сервер для розробки
├── package.json          # Налаштування пакетів
├── vercel.json           # Конфігурація Vercel
├── README.md             # Документація
└── public/               # Публічні ресурси
    ├── favicon.svg       # Іконка сайту
    ├── sitemap.xml       # Карта сайту
    └── site.webmanifest  # Маніфест для PWA
```

## Деплоймент на Vercel

### За допомогою Vercel CLI

1. Встановіть Vercel CLI глобально:
```bash
npm install -g vercel
```

2. Залогіньтесь у Vercel:
```bash
vercel login
```

3. Запустіть деплоймент з кореневої папки проекту:
```bash
vercel
```

4. Для продакшн деплойменту:
```bash
vercel --prod
```

### За допомогою Vercel Dashboard

1. Створіть обліковий запис на [Vercel](https://vercel.com) (якщо його немає)

2. Створіть новий проект і виберіть "Import Git Repository"

3. Підключіть свій GitHub репозиторій

4. Налаштуйте деплоймент:
   - Framework Preset: `Other`
   - Build Command: `npm run build`
   - Output Directory: `.`
   - Install Command: `npm install`

5. Натисніть "Deploy"

## Кастомізація

Для кастомізації проекту:

1. Змініть стилі у файлі `styles.css`
2. Відредагуйте вміст у файлі `index.html`
3. Модифікуйте JavaScript функціональність у файлі `script.js`

## Ліцензія

MIT 