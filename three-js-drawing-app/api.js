// Drawing API - Allows using drawing data in other applications

class DrawingAPI {
    constructor() {
        this.drawingData = null;
    }

    /**
     * Load drawing data from JSON
     * @param {string|Object} source - JSON string or object containing drawing data
     * @returns {boolean} - Success status
     */
    loadDrawing(source) {
        try {
            if (typeof source === 'string') {
                this.drawingData = JSON.parse(source);
            } else {
                this.drawingData = source;
            }
            return true;
        } catch (error) {
            console.error("Failed to load drawing:", error);
            return false;
        }
    }

    /**
     * Load drawing from file
     * @param {File} file - Drawing JSON file
     * @returns {Promise<boolean>} - Success status
     */
    loadDrawingFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    this.drawingData = JSON.parse(event.target.result);
                    resolve(true);
                } catch (error) {
                    console.error("Failed to parse drawing file:", error);
                    reject(error);
                }
            };
            reader.onerror = (error) => reject(error);
            reader.readAsText(file);
        });
    }

    /**
     * Render the drawing to a THREE.js scene
     * @param {THREE.Scene} scene - The scene to render to
     * @returns {Array<THREE.Line>} - Array of created line objects
     */
    renderToScene(scene) {
        if (!this.drawingData || !this.drawingData.lines) {
            console.error("No drawing data available");
            return [];
        }

        const lines = [];

        this.drawingData.lines.forEach(lineData => {
            // Create points
            const points = lineData.points.map(p => 
                new THREE.Vector3(p.x, p.y, p.z)
            );
            
            // Create geometry
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            
            // Create material
            const material = new THREE.LineBasicMaterial({
                color: lineData.color || 0x000000,
                linewidth: lineData.lineWidth || 1
            });
            
            // Create line
            const line = new THREE.Line(geometry, material);
            scene.add(line);
            lines.push(line);
        });

        return lines;
    }

    /**
     * Get a bitmap representation of the drawing
     * @param {number} width - Canvas width
     * @param {number} height - Canvas height 
     * @returns {HTMLCanvasElement} - Canvas element with the drawing
     */
    toBitmap(width = 800, height = 600) {
        if (!this.drawingData || !this.drawingData.lines) {
            console.error("No drawing data available");
            return null;
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, width, height);
        
        // Calculate center offset
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Draw each line
        this.drawingData.lines.forEach(lineData => {
            if (!lineData.points || lineData.points.length < 2) return;
            
            ctx.beginPath();
            ctx.strokeStyle = '#' + lineData.color.toString(16).padStart(6, '0');
            ctx.lineWidth = lineData.lineWidth || 1;
            
            // Convert first point from Three.js coordinates
            const firstPoint = lineData.points[0];
            ctx.moveTo(firstPoint.x + centerX, -firstPoint.y + centerY);
            
            // Draw remaining points
            for (let i = 1; i < lineData.points.length; i++) {
                const point = lineData.points[i];
                ctx.lineTo(point.x + centerX, -point.y + centerY);
            }
            
            ctx.stroke();
        });
        
        return canvas;
    }

    /**
     * Get drawing data as an array of strokes
     * @returns {Array} - Array of stroke data
     */
    getStrokes() {
        if (!this.drawingData || !this.drawingData.lines) {
            return [];
        }
        
        return this.drawingData.lines.map(line => ({
            points: line.points,
            color: line.color,
            width: line.lineWidth
        }));
    }
}

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DrawingAPI };
} else {
    window.DrawingAPI = DrawingAPI;
} 