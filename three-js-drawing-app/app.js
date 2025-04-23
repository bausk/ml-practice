// Three.js Drawing Interface

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);
const camera = new THREE.OrthographicCamera(
    window.innerWidth / -2, window.innerWidth / 2,
    window.innerHeight / 2, window.innerHeight / -2,
    0.1, 1000
);
camera.position.z = 5;

// Renderer setup
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Drawing state
let isDrawing = false;
let currentLine = null;
let linePoints = [];
let currentLineWidth = 3;
let currentColor = 0xFF0000;

// Drawing collection
const drawnLines = [];

// Handle window resize
window.addEventListener('resize', () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    camera.left = width / -2;
    camera.right = width / 2;
    camera.top = height / 2;
    camera.bottom = height / -2;
    camera.updateProjectionMatrix();
    
    renderer.setSize(width, height);
});

// Initialize a new line
function startLine(x, y) {
    linePoints = [];
    addPointToLine(x, y);
    
    const material = new THREE.LineBasicMaterial({ 
        color: currentColor,
        linewidth: currentLineWidth 
    });
    
    currentLine = new THREE.Line(
        new THREE.BufferGeometry(),
        material
    );
    
    scene.add(currentLine);
}

// Add point to current line
function addPointToLine(x, y) {
    // Convert from screen coordinates to Three.js coordinates
    const tx = x - window.innerWidth / 2;
    const ty = -y + window.innerHeight / 2;
    
    linePoints.push(new THREE.Vector3(tx, ty, 0));
    
    if (currentLine) {
        const geometry = new THREE.BufferGeometry().setFromPoints(linePoints);
        currentLine.geometry.dispose();
        currentLine.geometry = geometry;
    }
}

// Finalize current line
function endLine() {
    if (currentLine) {
        drawnLines.push({
            points: [...linePoints],
            color: currentColor,
            lineWidth: currentLineWidth
        });
        currentLine = null;
    }
}

// Clear the canvas
function clearCanvas() {
    drawnLines.forEach(line => {
        if (line.object && line.object.parent) {
            scene.remove(line.object);
            line.object.geometry.dispose();
            line.object.material.dispose();
        }
    });
    
    drawnLines.length = 0;
    render();
}

// Save drawing data
function saveDrawing() {
    const drawingData = {
        lines: drawnLines.map(line => ({
            points: line.points.map(p => ({ x: p.x, y: p.y, z: p.z })),
            color: line.color,
            lineWidth: line.lineWidth
        }))
    };
    
    const blob = new Blob([JSON.stringify(drawingData)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'drawing.json';
    a.click();
    
    URL.revokeObjectURL(url);
}

// Mouse and touch event handlers
function handlePointerDown(event) {
    isDrawing = true;
    startLine(event.clientX, event.clientY);
}

function handlePointerMove(event) {
    if (!isDrawing) return;
    addPointToLine(event.clientX, event.clientY);
    render();
}

function handlePointerUp() {
    if (isDrawing) {
        isDrawing = false;
        endLine();
    }
}

// Event listeners
renderer.domElement.addEventListener('pointerdown', handlePointerDown);
renderer.domElement.addEventListener('pointermove', handlePointerMove);
renderer.domElement.addEventListener('pointerup', handlePointerUp);
renderer.domElement.addEventListener('pointerleave', handlePointerUp);

// UI controls
document.getElementById('clear-btn').addEventListener('click', clearCanvas);
document.getElementById('save-btn').addEventListener('click', saveDrawing);
document.getElementById('line-width').addEventListener('input', function(e) {
    currentLineWidth = parseInt(e.target.value);
});

// Color buttons
document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const color = this.getAttribute('data-color');
        currentColor = parseInt(color.replace('#', '0x'));
        
        // Highlight selected color
        document.querySelectorAll('.color-btn').forEach(b => 
            b.style.border = '1px solid #000');
        this.style.border = '3px solid #000';
    });
});

// Set initial selected color
document.querySelector('.color-btn').style.border = '3px solid #000';

// Animation loop
function render() {
    renderer.render(scene, camera);
}

// Start rendering
render(); 