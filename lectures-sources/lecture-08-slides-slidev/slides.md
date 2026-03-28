---
theme: apple-basic
class: text-center
colorSchema: light
title: "Лекція 8: Від фотографій до ігрових світів"
info: |
  Лекція 8 — Модуль 2: Комп'ютерний зір для ігор.
  3D-реконструкція, детекція об'єктів та розуміння сцен.
transition: slide-left
drawings:
  persist: false
---

# Компʼютерний зір в іграх

<div class="abs-bl m-6 text-left text-sm opacity-60">
Лекція 8 — Штучний інтелект в ігрових застосунках<br>
Національний університет «Львівська Політехніка»
</div>

---
layout: center
---

# Задачі в індустрії і задачі компʼютерного зору

CNN аналізують зображення, але ігри (та роботи/UAV) живуть у **тривимірному просторі**.

| **Підгалузі розробки:** |
|--------------------|
| **Ігрові процеси**:  NPC-зір, аналіз кадрів у реальному часі, розпізнавання жестів і інтеракцій |
| **Процес розробки**: Автоматичне QA, пошук багів, класифікація контенту, створення ассетів |
| **Екосистема/Ops**: Аналіз стрімів, античіт, маркетинг |

---
layout: center
---

# Ігрові процеси





|  |
|--------------------|
| **Прогресивний ШІ**: Великі мовні моделі, трансформери, генеративний ШІ -> human-like bot systems |
| **Диверсифікація ігрового досвіду**: Не спроектовані поведінки і наратив, нові механіки і сенсори, недетермінований NPC AI |
| **Класичне машинне навчання**: Рекомендаційні системи, Процедурна генерація, NPC AI |
| **Експерименти**: Дослідження і техніки в майбутньому |

---
layout: center
---

# Приклади

<div class="flex items-center gap-4">
<img src="/images/gamecommands.jpeg" class="mx-auto h-72" />
<img src="/images/newsensor.jpeg" class="mx-auto h-72" />
</div>
---
layout: center
---

# Процеси розробки


|  |
|--------------------|
| **Прогресивний ШІ**: Генерація контенту і моделей, агентна генерація коду; тестування ідей, механік, карт |
| **Диверсифікація ігрового досвіду**: ---- |
| **Класичне машинне навчання**: Фотограмметрія сцен, предметів, персонажів; Навчання з підкріпленням |
| **Експерименти**: ---- |

---

# Інкрементальний SfM: 7 кроків

<img src="/images/02_sfm_pipeline.png" class="mx-auto h-56" />

<div class="grid grid-cols-3 gap-3 mt-4">
  <div class="border-l-4 border-blue-500 bg-white rounded p-3 shadow-sm text-sm">
    <strong>Кроки 1–3:</strong> Від пікселів до геометрії — знаходимо спільні точки між фотографіями
  </div>
  <div class="border-l-4 border-orange-500 bg-white rounded p-3 shadow-sm text-sm">
    <strong>Кроки 4–6:</strong> Нарощування моделі — додаємо нові камери та точки одну за одною
  </div>
  <div class="border-l-4 border-emerald-500 bg-white rounded p-3 shadow-sm text-sm">
    <strong>Крок 7:</strong> Глобальна оптимізація — уточнюємо все одразу (Bundle Adjustment)
  </div>
</div>

<p class="text-center text-sm text-gray-500 mt-3">Кроки 5–7 <strong>повторюються</strong> для кожного нового зображення</p>

---

# Від пікселів до геометрії (кроки 1–3)

<div class="space-y-3 mt-2">

<div class="flex items-center gap-4 bg-white border-l-4 border-blue-500 rounded-lg p-4 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">1</span>
  <div>
    <h3 class="font-bold">Виділення ознак</h3>
    <p class="text-sm text-gray-600">SIFT / SuperPoint знаходять точки, інваріантні до масштабу, повороту, освітлення. Кожна точка отримує числовий <strong>дескриптор</strong>.</p>
  </div>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-blue-500 rounded-lg p-4 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">2</span>
  <div>
    <h3 class="font-bold">Зіставлення (matching)</h3>
    <p class="text-sm text-gray-600">Порівняння дескрипторів між парами фото. Результат: «ця точка на фото A = ця точка на фото B».</p>
  </div>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-orange-500 rounded-lg p-4 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold">3</span>
  <div>
    <h3 class="font-bold">Геометрична верифікація</h3>
    <p class="text-sm text-gray-600">RANSAC оцінює <strong>фундаментальну матрицю</strong> — геометричне відношення між двома видами. Хибні пари (outliers) відкидаються.</p>
  </div>
</div>

</div>

<p class="text-center text-sm text-gray-500 mt-3">Результат: очищений <strong>граф сцени</strong> — які зображення пов'язані геометрично</p>

---

# Нарощування 3D-моделі (кроки 4–7)

<div class="space-y-3 mt-2">

<div class="flex items-center gap-4 bg-white border-l-4 border-orange-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold">4</span>
  <div>
    <h3 class="font-bold text-sm">Ініціалізація</h3>
    <p class="text-xs text-gray-600">Обрати пару фото з великою базою (baseline) → тріангулювати початкові 3D-точки.</p>
  </div>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-orange-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold">5</span>
  <div>
    <h3 class="font-bold text-sm">Реєстрація нових камер</h3>
    <p class="text-xs text-gray-600">Знайти відповідності з уже відомими 3D-точками → <strong>PnP</strong> (Perspective-n-Point) → поза камери.</p>
  </div>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-emerald-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold">6</span>
  <div>
    <h3 class="font-bold text-sm">Тріангуляція</h3>
    <p class="text-xs text-gray-600">Нова камера створює нові пари точок → обчислити нові 3D-координати → хмара зростає.</p>
  </div>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-emerald-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold">7</span>
  <div>
    <h3 class="font-bold text-sm">Bundle Adjustment</h3>
    <p class="text-xs text-gray-600">Глобальна оптимізація — уточнити <em>всі</em> пози камер та <em>всі</em> 3D-точки одночасно.</p>
  </div>
</div>

</div>

---

# Місце компʼютерного зору в екосистемі геймдеву

(CV, згорткові/конволюційні нейронні мережі)

| |
|-----|
| Процес розробки: Створення ассетів, катсцен, сцен, текстур (фотограмметрія)
| Процес розробки: Автоматизація QA і підтримки користувачів (детекція/сегментація)
| Геймплей: Заміна детермінистичних NPC (і гравця) поведінкою, що моделює природню
| Геймплей: Нові механіки

---

# SfM у контексті: споріднені методи

<img src="/images/03_comparison.png" class="mx-auto h-72" />

<div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-center text-sm">
  <strong>SfM — фундамент.</strong> NeRF і 3DGS використовують пози камер від COLMAP як вхідні дані. SfM дає «скелет», а нейронні методи — зовнішній вигляд.
</div>

---

## SfM (3DGS)

<div class="grid grid-cols-1 gap-8 mt-4">

<img src="/images/top_view_open.gif" />

</div>

---

# SfM у навігації дронів

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-blue-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Камеральна обробка <span class="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">SfM</span></h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li>Зйомка з перекриттям</li>
    <li>SfM + MVS на сервері</li>
    <li>Ортофотоплан + цифрова модель поверхні</li>
  </ul>
  <p class="text-xs text-gray-400 mt-2">Pix4D, OpenDroneMap, DJI Terra</p>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Під час польоту <span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold">SLAM</span></h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li>VIO: камера + IMU, 30+ Hz</li>
    <li>ORB-SLAM3, VINS-Mono</li>
    <li>SfM-карта як <em>апріорна</em> інформація</li>
  </ul>
  <p class="text-xs text-gray-400 mt-2">SfM надто повільний для live-уникнення перешкод</p>
</div>

</div>

<div class="mt-4 p-4 bg-rose-50 rounded-lg border border-rose-200">
  <strong class="text-rose-600">Проблема масштабу:</strong> монокулярний SfM не знає реальних розмірів. 1 м чи 10 м — для дрона це критично.
  <br><span class="text-sm">Розв'язання: GPS-мітки, IMU, відомі об'єкти.</span>
</div>

---

# Від реального світу до ігрового рівня

<img src="/images/04_photogrammetry_pipeline.png" class="mx-auto h-44" />

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-blue-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Хто це використовує</h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li><strong>EA DICE</strong> (Battlefield) — фотографування реальних локацій</li>
    <li><strong>Infinity Ward</strong> (CoD: MW) — сканування середовищ</li>
    <li><strong>DICE</strong> (Star Wars Battlefront) — скани декорацій фільму</li>
    <li><strong>Quixel Megascans</strong> (Epic) — 18 000+ сканованих ассетів</li>
  </ul>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm flex items-center justify-center">
  <p class="text-lg font-bold text-emerald-600 text-center">Економить місяці ручного 3D-моделювання</p>
</div>

</div>

---

# Нейронний рендеринг: NeRF та 3D Gaussian Splatting

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-violet-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-violet-600 font-bold">NeRF</h3>
  <p class="text-sm mt-2">Нейромережа вивчає функцію:</p>
  <div class="bg-violet-50 rounded p-2 text-center mt-2 font-mono text-sm">
    f(<b>x</b>, <b>d</b>) → (колір, щільність)
  </div>
  <div class="flex gap-2 mt-3">
    <span class="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold">Тренування: години</span>
    <span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-xs font-semibold">Рендер: сек/кадр</span>
  </div>
</div>

<div class="border-l-4 border-rose-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-rose-600 font-bold">3D Gaussian Splatting</h3>
  <p class="text-sm mt-2">Набір 3D-еліпсоїдів з кольором. Диференційована растеризація.</p>
  <div class="bg-rose-50 rounded p-2 text-center mt-2 text-sm">
    <strong>Тренування:</strong> 30–60 хв · <strong class="text-emerald-600">Рендер: 90+ FPS</strong>
  </div>
  <p class="text-xs text-gray-500 mt-2">glTF: <code>KHR_gaussian_splatting</code> (серпень 2025)</p>
</div>

</div>

<div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-center text-sm">
  Обидва методи використовують <strong>COLMAP-пози</strong> як вхід. SfM дає структуру — нейронні методи дають <strong>фотореалістичний вигляд</strong>.
</div>

---

# 3DGS для ігор: можливості та обмеження

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-rose-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-rose-600 font-bold">Чого немає</h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li>Полігональний меш → немає колізій</li>
    <li>Фізика — об'єкти не взаємодіють</li>
    <li>LOD — складно оптимізувати</li>
    <li>Обмежене редагування</li>
  </ul>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-emerald-600 font-bold">Де вже працює</h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li>Кінематографічні фони</li>
    <li>VR-середовища</li>
    <li>Швидкий прототипінг рівнів</li>
    <li>Превізуалізація</li>
  </ul>
</div>

</div>

### Гібридний конвеєр (поточна практика)

<img src="/images/09_hybrid_workflow.png" class="mx-auto h-36 mt-2" />

---
layout: section
---

# Нові механіки NPC AI
## Комп'ютерний зір у розробці ігор
Детекція об'єктів, сегментація, Vision Transformers

---

# Освіжувач: детекція і сегментація


<img src="/images/06_detection_vs_segmentation.png" class="mx-auto h-52" />

<div class="grid grid-cols-3 gap-4 mt-4 text-center">

<div class="border-t-4 border-blue-500 bg-white rounded-lg p-3 shadow-sm">
  <h3 class="font-bold text-blue-600">Класифікація</h3>
  <p class="text-sm text-gray-600">«На фото — кіт»</p>
  <p class="text-xs text-gray-400">1 мітка на зображення</p>
</div>

<div class="border-t-4 border-orange-500 bg-white rounded-lg p-3 shadow-sm">
  <h3 class="font-bold text-orange-600">Детекція</h3>
  <p class="text-sm text-gray-600">«Кіт — тут» (рамка)</p>
  <p class="text-xs text-gray-400">Рамки + класи + впевненість</p>
</div>

<div class="border-t-4 border-emerald-500 bg-white rounded-lg p-3 shadow-sm">
  <h3 class="font-bold text-emerald-600">Сегментація</h3>
  <p class="text-sm text-gray-600">«Ось ці пікселі — кіт»</p>
  <p class="text-xs text-gray-400">Попіксельна маска</p>
</div>

</div>

<p class="text-center text-sm mt-4">Три напрямки CV в іграх: <span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-xs font-semibold">Всередині гри</span> <span class="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">У розробці</span> <span class="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold">Навколо гри</span></p>

---

# Детекція об'єктів: YOLO та еволюція

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-blue-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Двоетапні (Two-stage)</h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li><strong>R-CNN</strong> (2014): Selective Search + CNN</li>
    <li><strong>Fast R-CNN</strong>: CNN один раз</li>
    <li><strong>Faster R-CNN</strong>: Region Proposal Network</li>
  </ul>
  <span class="inline-block mt-2 px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-xs font-semibold">~5 FPS — точно, але повільно</span>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Одноетапні (One-stage)</h3>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li><strong>YOLO</strong>: сітка S×S, один прохід</li>
    <li><strong>SSD</strong>: multi-scale feature maps</li>
    <li><strong>RetinaNet</strong>: Focal Loss</li>
  </ul>
  <span class="inline-block mt-2 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold">400+ FPS — реальний час!</span>
</div>

</div>

<div class="grid grid-cols-2 gap-4 mt-4">
  <div class="bg-white border-l-4 border-orange-500 rounded p-3 shadow-sm text-center text-sm">
    <strong>IoU</strong> (Intersection over Union) — метрика збігу рамок. IoU ≥ 0.5 → об'єкт «знайдено»
  </div>
  <div class="bg-white border-l-4 border-violet-500 rounded p-3 shadow-sm text-center text-sm">
    <strong>mAP</strong> — середня точність по класах. <strong>mAP@50:95</strong> — основний бенчмарк COCO
  </div>
</div>

---

# Детекція в іграх: 4 застосування

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-blue-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">NPC-зір <span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-xs">В грі</span></h3>
  <p class="text-sm text-gray-600 mt-1">Поступове розпізнавання, обмежене поле зору, контекстна обізнаність.</p>
  <p class="text-xs text-gray-400 mt-1">MineRL, MineDojo (NVIDIA)</p>
</div>

<div class="border-l-4 border-rose-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Античіт <span class="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-xs">Навколо</span></h3>
  <p class="text-sm text-gray-600 mt-1">Детекція оверлеїв, аналіз руху прицілу, відеоаналіз стрімів.</p>
  <p class="text-xs text-gray-400 mt-1">Riot Games, Easy Anti-Cheat</p>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Автоматичне QA <span class="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs">Розробка</span></h3>
  <p class="text-sm text-gray-600 mt-1">Графічні артефакти, z-fighting, UI-перевірка, порівняння білдів.</p>
  <p class="text-xs text-gray-400 mt-1">EA AutoPlay, Ubisoft La Forge</p>
</div>

<div class="border-l-4 border-orange-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="font-bold">Кіберспорт <span class="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-xs">Навколо</span></h3>
  <p class="text-sm text-gray-600 mt-1">Позиції гравців, теплові карти, highlight detection.</p>
  <p class="text-xs text-gray-400 mt-1">GRID / Bayes Esports</p>
</div>

</div>

---

# Три рівні сегментації

<div class="grid grid-cols-3 gap-4 mt-6">

<div class="border-t-4 border-blue-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold text-blue-600">Семантична</h3>
  <p class="text-sm text-gray-600 mt-2">Кожен піксель отримує <strong>клас</strong></p>
  <p class="text-xs text-gray-400 mt-1">«небо», «дорога», «дерево»</p>
</div>

<div class="border-t-4 border-orange-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold text-orange-600">Інстансна</h3>
  <p class="text-sm text-gray-600 mt-2">Кожен <strong>об'єкт окремо</strong></p>
  <p class="text-xs text-gray-400 mt-1">«авто #1», «авто #2»</p>
</div>

<div class="border-t-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold text-emerald-600">Паноптична</h3>
  <p class="text-sm text-gray-600 mt-2"><strong>Все разом:</strong> класи + інстанси</p>
  <p class="text-xs text-gray-400 mt-1">Повне розуміння сцени</p>
</div>

</div>

### Ключові архітектури

| Архітектура | Рік | Ключова ідея | Тип |
|---|---|---|---|
| **U-Net** | 2015 | Encoder-decoder + skip connections | Семантична |
| **DeepLab v3+** | 2018 | Atrous convolutions + ASPP | Семантична |
| **Mask R-CNN** | 2017 | Faster R-CNN + маска для кожної рамки | Інстансна |
| **SAM** | 2023 | Foundation model, 1.1B масок, zero-shot | Будь-яка |

---


---
layout: center
---

# Модальності компʼютерного зору

<img src="/images/tasks.jpeg" alt="Description" width="500" height="200">

---
# Модальності комп'ютерного зору

<div class="grid grid-cols-2 gap-4 mt-6">
<img src ="/images/tasks.jpeg" />
</div>

---

# Vision Transformer (ViT) та CLIP

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-violet-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-violet-600 font-bold">ViT / Swin / DETR</h3>
  <p class="text-sm mt-2">Зображення → патчі 16×16 → embedding → Transformer encoder</p>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li><strong>Swin</strong> (2021): локальні вікна, лінійна складність</li>
    <li><strong>DETR</strong> (2020): end-to-end детекція без NMS</li>
  </ul>
  <span class="inline-block mt-2 px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold">Глобальний контекст замість локальних згорток</span>
</div>

<div class="border-l-4 border-orange-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-orange-600 font-bold">CLIP: зір + мова</h3>
  <p class="text-sm mt-2">400M пар «зображення + текст» → спільний embedding-простір → zero-shot</p>
  <ul class="text-sm text-gray-600 mt-2 space-y-1">
    <li><strong>Пошук ассетів:</strong> «mossy stone wall» → знайде текстуру</li>
    <li><strong>Автокласифікація:</strong> жанр, настрій без тренування</li>
    <li><strong>Стилістика:</strong> перевірка відповідності арт-стилю</li>
  </ul>
</div>

</div>

<div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-center text-sm">
  <strong>Для ігор:</strong> глобальний контекст, гнучкість роздільності, природне поєднання з мовними моделями
</div>

---

# Оцінка глибини з одного фото

<div class="bg-white border-l-4 border-blue-500 rounded-lg p-4 shadow-sm text-center">
  <strong>Depth Anything v2</strong> (ByteDance, 2024) — 62M зображень, метрична глибина, реалтайм
</div>

<div class="grid grid-cols-3 gap-4 mt-6">

<div class="border-l-4 border-orange-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold">Normal maps</h3>
  <p class="text-sm text-gray-600 mt-2">2D текстура → карта глибини → автоматичний normal map для PBR</p>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold">2.5D ефекти</h3>
  <p class="text-sm text-gray-600 mt-2">Фото → глибина → паралакс для «живих» фонів у грі</p>
</div>

<div class="border-l-4 border-violet-500 bg-white rounded-lg p-4 shadow-sm text-center">
  <h3 class="font-bold">AR окклюзія</h3>
  <p class="text-sm text-gray-600 mt-2">Pokemon ховається за деревами завдяки depth map з камери</p>
</div>

</div>

<p class="text-center text-sm text-gray-500 mt-6">Моноколярна оцінка — дешевша альтернатива SfM для отримання <strong>приблизної</strong> 3D-інформації в реальному часі</p>

---
layout: section
---

# Частина III
## Від сканів до тренованих агентів
Реконструйовані середовища для RL

---

# Реконструйовані середовища для RL

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-rose-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-rose-600 font-bold">Проблема</h3>
  <p class="text-sm text-gray-600 mt-2">Тренування RL-агента потребує <strong>тисяч годин</strong> у 3D-середовищі. Моделювати вручну — дорого.</p>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-4 shadow-sm">
  <h3 class="text-emerald-600 font-bold">Рішення</h3>
  <p class="text-sm text-gray-600 mt-2">Відсканувати реальну будівлю → отримати <strong>готове тренувальне середовище</strong> за годину.</p>
</div>

</div>

<img src="/images/10_rl_pipeline.png" class="mx-auto h-36 mt-4" />

| Платформа | Опис | Дані |
|---|---|---|
| **Meta Habitat** | Швидкий 3D-симулятор для навігації | HM3D: 1000 сканів будівель |
| **Replica** (Meta) | Високоякісні скани з семантикою | 18 приміщень, HDR |
| **iGibson** (Stanford) | Інтерактивні сцени з фізикою | Готовий RL-код (SAC) |
| **AirSim** | UE5 як бекенд для RL | Будь-який UE5-рівень |

---

# Повний пайплайн розуміння сцени

<img src="/images/08_scene_pipeline.png" class="mx-auto h-48" />

<div class="grid grid-cols-2 gap-4 mt-4">

<div class="border-l-4 border-blue-500 bg-white rounded-lg p-3 shadow-sm">
  <h3 class="font-bold text-sm">Оптимізація для рушіїв</h3>
  <p class="text-xs text-gray-600 font-mono mt-1">PyTorch → torch.export → ONNX → TensorRT → C++ → GPU (< 5 мс)</p>
  <p class="text-xs text-gray-600 mt-1"><strong>Unity:</strong> Barracuda · <strong>UE5:</strong> NNE</p>
</div>

<div class="border-l-4 border-emerald-500 bg-white rounded-lg p-3 shadow-sm">
  <h3 class="font-bold text-sm">Що працює в реальному часі</h3>
  <p class="text-xs text-gray-600 mt-1"><strong>Так:</strong> YOLO-nano, Depth Anything-S, MediaPipe</p>
  <p class="text-xs text-gray-600"><strong>Ні (інструменти):</strong> SAM, Swin-L, Mask R-CNN</p>
</div>

</div>

---

# Кейси: CV у реальних іграх

| Проєкт | Технологія | Результат |
|---|---|---|
| **MineDojo** (NVIDIA) | MineCLIP (CLIP + відео) | Агент виконує текстові інструкції в Minecraft |
| **Ubisoft La Forge** | Детекція + сегментація | Автоматичне QA для Assassin's Creed |
| **MediaPipe** (Google) | Pose + Hand tracking | Just Dance, Beat Saber, Vision Pro |
| **GRID Esports** | YOLO на мінімапі | Автоматична аналітика CS/Dota 2 |
| **EA DICE** | Фотограмметрія + SfM | Реальні локації → ігрові карти Battlefield |
| **Quixel Megascans** | SfM + MVS | 18 000+ фотореалістичних ассетів для UE5 |

<div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-center text-sm">
  <strong>SLAM3R</strong> (CVPR 2025 Highlight): реконструкція 3D з відео через feed-forward нейромережу — без SfM чи bundle adjustment. Потенціал: генерація середовищ «на льоту» під час гри.
</div>

---

# Ключові висновки

<div class="space-y-3 mt-4">

<div class="flex items-center gap-4 bg-white border-l-4 border-blue-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">1</span>
  <p class="text-sm"><strong>SfM — фундамент</strong> усієї 3D-реконструкції: геометрія та пози камер з набору фотографій.</p>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-orange-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold">2</span>
  <p class="text-sm"><strong>Повний пайплайн:</strong> SfM → MVS → меш → рушій. NeRF і 3DGS дають фотореалістичний вигляд.</p>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-emerald-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold">3</span>
  <p class="text-sm"><strong>YOLO + сегментація</strong> — попіксельне розуміння для NPC-зору, QA, AR та процедурної генерації.</p>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-violet-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-violet-500 text-white flex items-center justify-center font-bold">4</span>
  <p class="text-sm"><strong>Vision Transformers + CLIP</strong> — глобальний контекст та зв'язок зору з мовою.</p>
</div>

<div class="flex items-center gap-4 bg-white border-l-4 border-rose-500 rounded-lg p-3 shadow-sm">
  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-rose-500 text-white flex items-center justify-center font-bold">5</span>
  <p class="text-sm"><strong>Реальні скани → ігрові рівні:</strong> економить місяці моделювання та дає середовища для RL-тренування.</p>
</div>

</div>

---
layout: center
class: text-center
---

# Наступна лекція

## Обробка послідовностей

RNN, LSTM, механізм уваги — від CV до NLP і назад

<div class="flex gap-3 justify-center mt-8">
  <span class="px-3 py-1 rounded-full bg-gray-200 text-gray-700 text-sm font-semibold">Часові ряди</span>
  <span class="px-3 py-1 rounded-full bg-gray-200 text-gray-700 text-sm font-semibold">Діалогові системи</span>
  <span class="px-3 py-1 rounded-full bg-gray-200 text-gray-700 text-sm font-semibold">Transformer</span>
</div>
