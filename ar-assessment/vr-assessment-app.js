// VR Competency Assessment Application
// Додаток для оцінювання компетентностей з віртуальної реальності

// Використовуємо Three.js для 3D візуалізації
import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// Клас інтерактивного додатку для оцінювання
class VRCompetencyAssessment {
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
        
        // Ініціалізація контролерів VR
        this.initVRControllers();
        
        // Створення інтерактивних зон для завдань
        this.createTaskZones();
        
        // Ініціалізація системи оцінювання
        this.initAssessmentSystem();
        
        // Запуск анімаційного циклу
        this.renderer.setAnimationLoop(this.render.bind(this));
        
        // Обробник зміни розміру вікна
        window.addEventListener('resize', this.onWindowResize.bind(this));
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
        
        const controllerModelFactory = new THREE.GLTFLoader();
        
        // Додавання видимих моделей для контролерів
        const controllerGeometry = new THREE.BoxGeometry(0.05, 0.05, 0.2);
        const controllerMaterial = new THREE.MeshStandardMaterial({ color: 0xff0000 });
        
        const controllerMesh1 = new THREE.Mesh(controllerGeometry, controllerMaterial);
        controllerMesh1.position.z = -0.1;
        this.controller1.add(controllerMesh1);
        
        const controllerMesh2 = new THREE.Mesh(controllerGeometry, controllerMaterial);
        controllerMesh2.position.z = -0.1;
        this.controller2.add(controllerMesh2);
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
        
        // Створення текстової мітки
        const textGeometry = new THREE.TextGeometry(taskType, {
            font: new THREE.Font(), // Потрібно завантажити шрифт
            size: 0.2,
            height: 0.05
        });
        const textMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
        const textMesh = new THREE.Mesh(textGeometry, textMaterial);
        textMesh.position.set(-0.5, 0.5, 0);
        // group.add(textMesh); // Закоментовано, бо потрібно спочатку завантажити шрифт
        
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
        // Код для створення HUD буде тут
        console.log("HUD created");
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
        
        // Тут буде код для відображення питання в VR
    }
    
    // Обробка взаємодії під час виконання завдання
    handleTaskInteraction(controller) {
        // Код для обробки взаємодії під час виконання завдання
    }
    
    // Завершення поточного завдання
    completeTask() {
        console.log(`Task ${this.currentTask} completed with score: ${this.scores[this.currentTask]}`);
        this.currentTask = null;
        
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
        
        // Тут буде код для відображення підсумкових результатів у VR
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

// Запуск додатку
document.addEventListener('DOMContentLoaded', () => {
    const app = new VRCompetencyAssessment();
});
