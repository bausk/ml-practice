// VR Competency Assessment Application
// Додаток для оцінювання компетентностей з віртуальної реальності

// Використовуємо Three.js для 3D візуалізації
import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
// Remove FontLoader and TextGeometry imports
// import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
// import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';

// Import our TextHelper instead
import TextHelper from './utils/TextHelper.js';

// Клас інтерактивного додатку для оцінювання
export class VRCompetencyAssessment {
    constructor() {
        // Налаштування сцени
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x505050);
        
        // Налаштування камери
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 1.6, 3);
        
        // Налаштування рендерера
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.xr.enabled = true;
        document.body.appendChild(this.renderer.domElement);
        
        // Додавання кнопки для VR режиму
        document.body.appendChild(VRButton.createButton(this.renderer));
        
        // Налаштування контролерів для орбітальної камери
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.target.set(0, 1.6, 0);
        this.controls.update();
        
        // Налаштування світла
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 10, 0);
        this.scene.add(directionalLight);
        
        // Додавання підлоги
        const floorGeometry = new THREE.PlaneGeometry(20, 20);
        const floorMaterial = new THREE.MeshStandardMaterial({ color: 0x808080 });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        this.scene.add(floor);
        
        // Initialize task zones directly (no font loading needed)
        this.initVRControllers();
        this.createTaskZones();
        this.initAssessmentSystem();
        
        // Запуск анімаційного циклу
        this.renderer.setAnimationLoop(this.render.bind(this));
        
        // Обробник зміни розміру вікна
        window.addEventListener('resize', this.onWindowResize.bind(this));
    }
    
    // Remove loadFonts method since we don't need it anymore
    // loadFonts() { ... }
    
    // Replace updateTaskZoneLabels with a version that uses TextHelper
    updateTaskZoneLabels() {
        if (!this.taskZones) return;
        
        // Update each task zone with label
        this.taskZones.forEach(zone => {
            // Видалення старого текстового меша, якщо він існує
            const oldTextMesh = zone.children.find(child => child.userData && child.userData.isLabel);
            if (oldTextMesh) {
                zone.remove(oldTextMesh);
            }
            
            // Створення нового текстового спрайта
            const taskType = zone.userData.taskType;
            
            // Create text sprite with TextHelper - with wider text for better Cyrillic readability
            const textSprite = TextHelper.createTextSprite(taskType, {
                fontFamily: "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif",  // PT Sans is wider and better for Cyrillic
                fontSize: 64,
                fontWeight: 'bold',
                fillColor: 'white',
                padding: 20,
                // letterSpacing: 0,  // Add letter spacing for wider appearance
                // widthFactor: 2.3   // Increase from 1.25 to 1.3 for better readability
            });
            
            textSprite.position.set(0, 0.7, 0);
            textSprite.scale.set(1.5, 0.5, 1);
            textSprite.userData = { isLabel: true };
            
            zone.add(textSprite);
        });
    }
    
    // Ініціалізація VR контролерів
    initVRControllers() {
        this.controller1 = this.renderer.xr.getController(0);
        this.controller1.addEventListener('selectstart', this.onSelectStart.bind(this));
        this.controller1.addEventListener('selectend', this.onSelectEnd.bind(this));
        this.scene.add(this.controller1);
        
        this.controller2 = this.renderer.xr.getController(1);
        this.controller2.addEventListener('selectstart', this.onSelectStart.bind(this));
        this.controller2.addEventListener('selectend', this.onSelectEnd.bind(this));
        this.scene.add(this.controller2);
        
        // Додавання видимих моделей для контролерів
        const controllerGeometry = new THREE.BoxGeometry(0.05, 0.05, 0.2);
        const controllerMaterial = new THREE.MeshStandardMaterial({ color: 0xff0000 });
        
        const controllerMesh1 = new THREE.Mesh(controllerGeometry, controllerMaterial);
        controllerMesh1.position.z = -0.1;
        this.controller1.add(controllerMesh1);
        
        const controllerMesh2 = new THREE.Mesh(controllerGeometry, controllerMaterial);
        controllerMesh2.position.z = -0.1;
        this.controller2.add(controllerMesh2);
        
        // Додавання променів для вказування
        const geometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 0, -5)
        ]);
        
        const material = new THREE.LineBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.5
        });
        
        const line1 = new THREE.Line(geometry, material);
        line1.name = 'line';
        this.controller1.add(line1);
        
        const line2 = new THREE.Line(geometry, material);
        line2.name = 'line';
        this.controller2.add(line2);
    }
    
    // Створення інтерактивних зон для різних завдань
    createTaskZones() {
        this.taskZones = [];
        const taskTypes = [
            "3D Моделювання", 
            "Інтерфейс VR", 
            "Фізика VR", 
            "Оптимізація", 
            "Взаємодія"
        ];
        
        for (let i = 0; i < taskTypes.length; i++) {
            const angle = (i / taskTypes.length) * Math.PI * 2;
            const radius = 5;
            
            const x = Math.sin(angle) * radius;
            const z = Math.cos(angle) * radius;
            
            // Створення зони завдання
            const taskZone = this.createTaskZone(x, 1, z, taskTypes[i]);
            this.taskZones.push(taskZone);
            this.scene.add(taskZone);
        }
        
        // Add labels immediately
        this.updateTaskZoneLabels();
    }
    
    // Створення окремої зони завдання
    createTaskZone(x, y, z, taskType) {
        const group = new THREE.Group();
        group.position.set(x, y, z);
        group.userData = { taskType: taskType, interactive: true };
        
        // Створення платформи
        const platformGeometry = new THREE.CylinderGeometry(1, 1, 0.1, 32);
        const platformMaterial = new THREE.MeshStandardMaterial({ color: 0x4444aa });
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.y = -0.05;
        group.add(platform);
        
        // Створення об'єкта-індикатора для кожної зони
        const indicatorGeometry = new THREE.SphereGeometry(0.2, 32, 32);
        const indicatorMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff00, transparent: true, opacity: 0.7 });
        const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial);
        indicator.position.y = 1;
        group.add(indicator);
        
        return group;
    }
    
    // Ініціалізація системи оцінювання
    initAssessmentSystem() {
        this.scores = {
            "3D Моделювання": 0,
            "Інтерфейс VR": 0,
            "Фізика VR": 0,
            "Оптимізація": 0,
            "Взаємодія": 0
        };
        
        this.currentTask = null;
        this.assessmentComplete = false;
        this.currentQuestionIndex = 0;
        
        // Питання для оцінювання за категоріями
        this.questions = {
            "3D Моделювання": [
                {
                    question: "Який формат найкраще підходить для обміну 3D моделями у VR проектах?",
                    options: ["FBX", "glTF", "OBJ", "STL"],
                    correctAnswer: 1,
                    explanation: "glTF є відкритим стандартом, оптимізованим для передачі 3D моделей через мережу та їх відображення у реальному часі."
                },
                {
                    question: "Що таке LOD у контексті 3D моделювання для VR?",
                    options: ["Light Occlusion Design", "Level of Detail", "Low Object Displacement", "Layered Object Design"],
                    correctAnswer: 1,
                    explanation: "Level of Detail (рівень деталізації) - це техніка, яка використовує різні версії моделі з різним ступенем деталізації залежно від відстані до камери."
                },
                {
                    question: "Яка рекомендована кількість полігонів для інтерактивного об'єкта у VR?",
                    options: ["100-500", "1,000-10,000", "50,000-100,000", "Понад 1,000,000"],
                    correctAnswer: 1,
                    explanation: "Для VR рекомендується використовувати моделі з оптимізованою кількістю полігонів (1,000-10,000) для забезпечення плавної роботи."
                }
            ],
            "Інтерфейс VR": [
                {
                    question: "Яка рекомендована відстань для розміщення елементів інтерфейсу у VR?",
                    options: ["0.5-1 метр", "1-2 метри", "3-5 метрів", "Більше 10 метрів"],
                    correctAnswer: 1,
                    explanation: "Елементи інтерфейсу у VR найкраще розміщувати на відстані 1-2 метри від користувача для комфортного сприйняття."
                },
                {
                    question: "Який тип взаємодії найбільш природний для VR інтерфейсів?",
                    options: ["Клавіатурний ввід", "Вказівна взаємодія (point-and-click)", "Жестова взаємодія", "Голосові команди"],
                    correctAnswer: 2,
                    explanation: "Жестова взаємодія є найбільш природним способом взаємодії у VR, оскільки вона відповідає тому, як люди взаємодіють з об'єктами у реальному світі."
                },
                {
                    question: "Яке правило дизайну VR інтерфейсів допомагає зменшити дискомфорт користувача?",
                    options: ["Використовувати яскраві кольори", "Розміщувати елементи в периферійному зорі", "Уникати швидких рухів елементів інтерфейсу", "Постійно змінювати масштаб елементів"],
                    correctAnswer: 2,
                    explanation: "Швидкі рухи елементів інтерфейсу можуть спричинити кінетоз (motion sickness), тому їх слід уникати."
                }
            ],
            "Фізика VR": [
                {
                    question: "Який мінімальний FPS (кадрів за секунду) рекомендується для комфортного VR досвіду?",
                    options: ["30 FPS", "60 FPS", "90 FPS", "120 FPS"],
                    correctAnswer: 2,
                    explanation: "Для комфортного VR досвіду рекомендується мінімум 90 FPS, щоб уникнути затримок та запобігти кінетозу."
                },
                {
                    question: "Що таке 'teleportation' у контексті VR?",
                    options: ["Техніка рендерингу об'єктів", "Механіка переміщення користувача", "Метод синхронізації даних", "Алгоритм відстеження руху"],
                    correctAnswer: 1,
                    explanation: "Teleportation - це механіка переміщення, яка дозволяє користувачу миттєво переміщатися між різними точками віртуального простору, що допомагає уникнути кінетозу."
                },
                {
                    question: "Як правильно реалізувати гравітацію у VR додатку?",
                    options: ["Завжди використовувати реалістичну земну гравітацію", "Повністю вимкнути гравітацію", "Адаптувати гравітацію залежно від сценарію використання", "Завжди використовувати місячну гравітацію"],
                    correctAnswer: 2,
                    explanation: "Гравітацію слід адаптувати залежно від сценарію використання VR додатку, враховуючи комфорт користувача та вимоги до реалізму."
                }
            ],
            "Оптимізація": [
                {
                    question: "Яка техніка рендерингу найбільш ефективна для VR?",
                    options: ["Forward Rendering", "Deferred Rendering", "Ray Tracing", "Screen Space Ambient Occlusion"],
                    correctAnswer: 0,
                    explanation: "Forward Rendering часто є найбільш ефективним для VR через меншу затримку та кращу підтримку прозорості й антиаліасингу."
                },
                {
                    question: "Яка техніка найбільш ефективна для оптимізації VR сцени з багатьма об'єктами?",
                    options: ["Збільшення розміру текстур", "Static Batching", "Використання складніших шейдерів", "Збільшення кількості джерел світла"],
                    correctAnswer: 1,
                    explanation: "Static Batching - об'єднання статичних об'єктів в один меш, що зменшує кількість викликів рендерингу."
                },
                {
                    question: "Як найкраще оптимізувати освітлення у VR сцені?",
                    options: ["Використовувати лише динамічні джерела світла", "Запікати освітлення для статичних об'єктів", "Вимкнути всі тіні", "Використовувати лише точкові джерела світла"],
                    correctAnswer: 1,
                    explanation: "Запікання освітлення (light baking) для статичних об'єктів дозволяє зменшити обчислювальне навантаження під час роботи програми."
                }
            ],
            "Взаємодія": [
                {
                    question: "Яка технологія використовується для відстеження положення рук у сучасних VR системах?",
                    options: ["Тільки гіроскопи", "Ультразвукові сенсори", "Оптичне відстеження з маркерами", "Комбінація камер та інерційних сенсорів"],
                    correctAnswer: 3,
                    explanation: "Сучасні VR системи використовують комбінацію камер (включаючи інфрачервоні) та інерційних сенсорів для точного відстеження положення та руху рук."
                },
                {
                    question: "Що таке 'haptic feedback' у VR?",
                    options: ["Візуальний відгук", "Звуковий відгук", "Тактильний відгук", "Тепловий відгук"],
                    correctAnswer: 2,
                    explanation: "Haptic feedback (тактильний відгук) - це технологія, яка симулює відчуття дотику, вібрації або руху, щоб підвищити рівень занурення користувача."
                },
                {
                    question: "Яка стратегія є найкращою для запобігання кінетозу у VR?",
                    options: ["Швидкі рухи камери", "Використання різких переходів між сценами", "Надання користувачу контролю над рухом", "Постійні зміни масштабу об'єктів"],
                    correctAnswer: 2,
                    explanation: "Надання користувачу контролю над рухом зменшує когнітивний дисонанс між тим, що бачить користувач, і тим, що відчуває його вестибулярний апарат."
                }
            ]
        };
        
        // Створення HUD для відображення інформації
        this.createHUD();
    }
    
    // Створення HUD (heads-up display) для відображення інформації
    createHUD() {
        // Створення контейнера для HUD
        this.hudElement = document.createElement('div');
        this.hudElement.className = 'vr-hud';
        this.hudElement.style.display = 'none';
        this.hudElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        this.hudElement.style.letterSpacing = "1px";
        document.body.appendChild(this.hudElement);
        
        // Створення елементів для відображення питань
        this.questionElement = document.createElement('div');
        this.questionElement.className = 'vr-question';
        this.questionElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        this.questionElement.style.letterSpacing = "1px";
        this.questionElement.style.wordSpacing = "2px";
        this.hudElement.appendChild(this.questionElement);
        
        // Створення контейнера для варіантів відповідей
        this.optionsContainer = document.createElement('div');
        this.optionsContainer.className = 'vr-options';
        this.hudElement.appendChild(this.optionsContainer);
        
        // Створення елемента для відображення пояснення
        this.explanationElement = document.createElement('div');
        this.explanationElement.className = 'vr-explanation';
        this.explanationElement.style.display = 'none';
        this.explanationElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        this.explanationElement.style.letterSpacing = "1px";
        this.hudElement.appendChild(this.explanationElement);
    }
    
    // Відображення HUD для питань та відповідей
    showQuestionHUD(question) {
        // Оновлення тексту питання
        this.questionElement.textContent = question.question;
        
        // Очищення контейнера варіантів
        this.optionsContainer.innerHTML = '';
        
        // Додавання варіантів відповідей
        question.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'vr-option';
            optionElement.textContent = option;
            optionElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
            optionElement.style.letterSpacing = "1px";
            optionElement.style.wordSpacing = "2px";
            optionElement.dataset.index = index;
            this.optionsContainer.appendChild(optionElement);
        });
        
        // Показ HUD
        this.hudElement.style.display = 'flex';
        this.explanationElement.style.display = 'none';
    }
    
    // Обробник події натискання на кнопку контролера
    onSelectStart(event) {
        const controller = event.target;
        const intersection = this.getIntersection(controller);
        
        if (intersection && intersection.object.parent.userData.interactive) {
            this.startTask(intersection.object.parent.userData.taskType);
        }
        
        if (this.currentTask) {
            this.handleTaskInteraction(controller);
        }
    }
    
    // Обробник закінчення натискання на кнопку контролера
    onSelectEnd(event) {
        // Код для обробки закінчення натискання
    }
    
    // Отримання перетину променя з об'єктами сцени
    getIntersection(controller) {
        const tempMatrix = new THREE.Matrix4();
        tempMatrix.identity().extractRotation(controller.matrixWorld);
        
        const raycaster = new THREE.Raycaster();
        raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
        raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
        
        return raycaster.intersectObjects(this.scene.children, true)[0];
    }
    
    // Початок виконання завдання
    startTask(taskType) {
        if (this.currentTask === taskType) return;
        
        console.log(`Starting task: ${taskType}`);
        this.currentTask = taskType;
        this.currentQuestionIndex = 0;
        
        // Відображення поточного питання
        this.displayCurrentQuestion();
    }
    
    // Відображення поточного питання
    displayCurrentQuestion() {
        if (!this.currentTask) return;
        
        const questions = this.questions[this.currentTask];
        if (this.currentQuestionIndex >= questions.length) {
            this.completeTask();
            return;
        }
        
        const question = questions[this.currentQuestionIndex];
        console.log(`Question: ${question.question}`);
        console.log(`Options: ${question.options.join(", ")}`);
        
        // Відображення питання в HUD
        this.showQuestionHUD(question);
    }
    
    // Обробка взаємодії під час виконання завдання
    handleTaskInteraction(controller) {
        const intersection = this.getIntersection(controller);
        
        if (intersection && intersection.object.classList && intersection.object.classList.contains('vr-option')) {
            const selectedIndex = parseInt(intersection.object.dataset.index);
            this.submitAnswer(selectedIndex);
        }
    }
    
    // Відправка відповіді
    submitAnswer(selectedIndex) {
        if (!this.currentTask) return;
        
        const questions = this.questions[this.currentTask];
        const question = questions[this.currentQuestionIndex];
        
        // Перевірка правильності відповіді
        const isCorrect = selectedIndex === question.correctAnswer;
        
        if (isCorrect) {
            this.scores[this.currentTask]++;
        }
        
        // Відображення пояснення
        this.explanationElement.textContent = question.explanation;
        this.explanationElement.style.display = 'block';
        
        // Виділення вибраної відповіді
        const options = this.optionsContainer.querySelectorAll('.vr-option');
        options.forEach((option, index) => {
            if (index === selectedIndex) {
                option.classList.add('selected');
            }
        });
        
        // Перехід до наступного питання через деякий час
        setTimeout(() => {
            this.currentQuestionIndex++;
            this.displayCurrentQuestion();
        }, 3000);
    }
    
    // Завершення поточного завдання
    completeTask() {
        console.log(`Task ${this.currentTask} completed with score: ${this.scores[this.currentTask]}`);
        this.currentTask = null;
        
        // Сховати HUD
        this.hudElement.style.display = 'none';
        
        // Перевірка, чи всі завдання виконані
        if (Object.values(this.scores).every(score => score > 0)) {
            this.completeAssessment();
        }
    }
    
    // Завершення всього оцінювання
    completeAssessment() {
        if (this.assessmentComplete) return;
        
        this.assessmentComplete = true;
        console.log("Assessment completed!");
        console.log("Final scores:", this.scores);
        
        // Обчислення загального балу
        const totalScore = Object.values(this.scores).reduce((sum, score) => sum + score, 0);
        const maxScore = Object.keys(this.scores).length * 3; // 3 питання в кожній категорії
        const percentage = (totalScore / maxScore) * 100;
        
        console.log(`Total score: ${totalScore}/${maxScore} (${percentage.toFixed(2)}%)`);
        
        // Відображення результатів на веб-сторінці
        this.showResults();
    }
    
    // Відображення результатів оцінювання
    showResults() {
        if (!this.scores) return;
        
        // Create or get the score display element
        let scoreDisplay = document.getElementById('scoreDisplay');
        if (!scoreDisplay) {
            scoreDisplay = document.createElement('div');
            scoreDisplay.id = 'scoreDisplay';
            scoreDisplay.style.position = 'absolute';
            scoreDisplay.style.top = '50%';
            scoreDisplay.style.left = '50%';
            scoreDisplay.style.transform = 'translate(-50%, -50%)';
            scoreDisplay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            scoreDisplay.style.color = 'white';
            scoreDisplay.style.padding = '30px';
            scoreDisplay.style.borderRadius = '15px';
            scoreDisplay.style.zIndex = '1000';
            scoreDisplay.style.maxWidth = '500px';
            scoreDisplay.style.width = '80%';
            scoreDisplay.style.textAlign = 'center';
            
            // Ensure we use a Cyrillic-compatible font with wider text
            scoreDisplay.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
            scoreDisplay.style.letterSpacing = "1px";
            
            document.body.appendChild(scoreDisplay);
        }
        
        // Add title
        const title = document.createElement('h2');
        title.textContent = 'Результати оцінювання компетентностей';
        title.style.color = '#4cc9f0';
        title.style.marginBottom = '20px';
        title.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        title.style.letterSpacing = "1.5px";
        title.style.fontWeight = "bold";
        scoreDisplay.appendChild(title);
        
        // Add scores container
        const scoresContainer = document.createElement('div');
        scoresContainer.style.marginBottom = '20px';
        scoreDisplay.appendChild(scoresContainer);
        
        // Add each score category
        let totalScore = 0;
        let maxScore = 0;
        
        // Clear the scores container
        scoresContainer.innerHTML = '';
        
        Object.entries(this.scores).forEach(([category, { score, total }]) => {
            const scoreItem = document.createElement('div');
            scoreItem.className = 'score-item';
            scoreItem.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
            scoreItem.style.letterSpacing = "1px";
            scoreItem.style.marginBottom = '10px';
            
            const categoryElement = document.createElement('div');
            categoryElement.className = 'score-category';
            categoryElement.textContent = category;
            categoryElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
            categoryElement.style.letterSpacing = "1px";
            categoryElement.style.fontWeight = "bold";
            categoryElement.style.marginBottom = '5px';
            
            const scoreValue = document.createElement('div');
            scoreValue.className = 'score-value';
            scoreValue.textContent = `${score}/${total}`;
            scoreValue.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
            scoreValue.style.letterSpacing = "1px";
            scoreValue.style.marginBottom = '5px';
            
            // Score visualization
            const visualizationContainer = document.createElement('div');
            visualizationContainer.className = 'score-visualization-container';
            visualizationContainer.style.width = '100%';
            visualizationContainer.style.marginBottom = '10px';
            
            const visualization = document.createElement('div');
            visualization.className = 'score-visualization';
            visualization.style.height = '12px';
            visualization.style.backgroundColor = '#e0e0e0';
            visualization.style.borderRadius = '6px';
            visualization.style.overflow = 'hidden';
            
            const percentage = (score / total) * 100;
            const progress = document.createElement('div');
            progress.style.width = `${percentage}%`;
            progress.style.height = '100%';
            progress.style.backgroundColor = '#4cc9f0';
            progress.style.borderRadius = '6px';
            
            visualization.appendChild(progress);
            visualizationContainer.appendChild(visualization);
            
            scoreItem.appendChild(categoryElement);
            scoreItem.appendChild(scoreValue);
            scoreItem.appendChild(visualizationContainer);
            scoresContainer.appendChild(scoreItem);
            
            totalScore += score;
            maxScore += total;
        });
        
        // Add total score
        const totalScoreElement = document.createElement('div');
        totalScoreElement.className = 'total-score';
        const percentage = (totalScore / maxScore) * 100;
        
        // Відображення загального балу с поддержкой кириллицы
        totalScoreElement.textContent = `Загальний бал: ${totalScore}/${maxScore} (${percentage.toFixed(1)}%)`;
        totalScoreElement.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        totalScoreElement.style.letterSpacing = "1px";
        totalScoreElement.style.fontWeight = "bold";
        totalScoreElement.style.fontSize = "1.2em";
        totalScoreElement.style.marginTop = "20px";
        
        scoreDisplay.appendChild(totalScoreElement);
        
        // Add button to close results
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Закрити';
        closeButton.style.marginTop = '20px';
        closeButton.style.padding = '10px 20px';
        closeButton.style.backgroundColor = '#4cc9f0';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '5px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif";
        closeButton.style.letterSpacing = "1px";
        closeButton.style.fontWeight = "bold";
        
        closeButton.addEventListener('click', () => {
            scoreDisplay.remove();
        });
        
        scoreDisplay.appendChild(closeButton);
    }
    
    // Обробник зміни розміру вікна
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    // Функція рендерингу
    render() {
        this.renderer.render(this.scene, this.camera);
    }
} 