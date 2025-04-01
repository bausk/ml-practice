// Main entry point for the VR Competency Assessment application
import './styles/main.css';
import { VRCompetencyAssessment } from './vr-assessment-app';
import Stats from 'stats.js';

// Initialize performance monitoring
let stats;
if (process.env.NODE_ENV !== 'production') {
    stats = new Stats();
    stats.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
    document.body.appendChild(stats.dom);
}

// Manage loading state
const loadingElement = document.getElementById('loading');
window.addEventListener('load', () => {
    setTimeout(() => {
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }, 1000);
});

// Check WebXR support
function checkXRSupport() {
    if ('xr' in navigator) {
        navigator.xr.isSessionSupported('immersive-vr')
            .then((supported) => {
                if (!supported) {
                    showUnsupportedMessage("Your browser supports WebXR but not immersive VR sessions");
                }
            })
            .catch(err => {
                showUnsupportedMessage("Error checking VR support: " + err.message);
            });
    } else {
        showUnsupportedMessage("WebXR is not supported by your browser");
    }
}

function showUnsupportedMessage(message) {
    const infoElement = document.getElementById('info');
    if (infoElement) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'warning-message';
        warningDiv.textContent = message;
        infoElement.appendChild(warningDiv);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Check XR support
    checkXRSupport();
    
    // Initialize the VR application
    const app = new VRCompetencyAssessment();
    
    // Animation loop for performance monitoring
    if (stats) {
        function animate() {
            stats.begin();
            stats.end();
            requestAnimationFrame(animate);
        }
        animate();
    }
}); 