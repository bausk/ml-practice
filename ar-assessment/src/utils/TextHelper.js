import * as THREE from 'three';

/**
 * TextHelper class for rendering text with full Unicode support (including Cyrillic)
 * Uses HTML Canvas to render text and then converts it to a texture for Three.js
 */
export class TextHelper {
    /**
     * Create text as a sprite using Canvas for full language support
     * 
     * @param {string} text - The text to render
     * @param {Object} options - Configuration options
     * @param {string} options.fontFamily - Font family to use (default: 'Arial')
     * @param {number} options.fontSize - Font size in pixels (default: 32)
     * @param {string} options.fontWeight - Font weight (default: 'normal')
     * @param {string} options.fillColor - Text color (default: 'white')
     * @param {string} options.backgroundColor - Background color (default: 'transparent')
     * @param {number} options.padding - Padding around text in pixels (default: 10)
     * @param {number} options.letterSpacing - Additional spacing between letters in pixels (default: 0)
     * @param {number} options.widthFactor - Factor to artificially widen the text (default: 1.0)
     * @returns {THREE.Sprite} - A Three.js sprite with the text
     */
    static createTextSprite(
        text,
        {
            fontFamily = "'PT Sans', 'Roboto', 'Noto Sans', Arial, sans-serif",
            fontSize = 32,
            fontWeight = 'normal',
            fillStyle = '#ffffff',
            backgroundColor = 'rgba(0, 0, 0, 0.5)',
            padding = 10,
            letterSpacing = 0,
            widthFactor = 1.0
        } = {}
    ) {
        // Create canvas element
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        // Set font properties
        context.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
        
        // Calculate dimensions with letter spacing
        let totalWidth = 0;
        let maxHeight = fontSize;
        
        // If letter spacing is enabled, we need to measure and place each character manually
        if (letterSpacing > 0) {
            for (let i = 0; i < text.length; i++) {
                const metrics = context.measureText(text[i]);
                totalWidth += metrics.width + letterSpacing;
                const height = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
                maxHeight = Math.max(maxHeight, height);
            }
            // Remove the last extra letter spacing
            if (text.length > 0) {
                totalWidth -= letterSpacing;
            }
        } else {
            // Standard measurement if no letter spacing
            const metrics = context.measureText(text);
            totalWidth = metrics.width;
        }
        
        // Apply width factor to make text wider
        totalWidth *= widthFactor;
        
        // Set canvas dimensions with padding
        canvas.width = totalWidth + padding * 2;
        canvas.height = maxHeight + padding * 2;
        
        // Clear and fill background if needed
        context.clearRect(0, 0, canvas.width, canvas.height);
        if (backgroundColor !== 'transparent') {
            context.fillStyle = backgroundColor;
            context.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        // Set text properties
        context.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
        context.fillStyle = fillStyle;
        
        // Draw text with custom letter spacing if needed
        if (letterSpacing > 0) {
            let xPosition = padding;
            const yPosition = padding + maxHeight / 2;
            
            context.textBaseline = 'middle';
            
            // Draw each character with the specified spacing
            for (let i = 0; i < text.length; i++) {
                const char = text[i];
                const charWidth = context.measureText(char).width;
                
                // Stretch the characters horizontally if width factor is > 1
                if (widthFactor > 1.0) {
                    context.save();
                    context.translate(xPosition, yPosition);
                    context.scale(widthFactor, 1);
                    context.fillText(char, 0, 0);
                    context.restore();
                    xPosition += (charWidth * widthFactor) + letterSpacing;
                } else {
                    context.fillText(char, xPosition, yPosition);
                    xPosition += charWidth + letterSpacing;
                }
            }
        } else {
            // Standard centered text drawing if no letter spacing
            context.textBaseline = 'middle';
            context.textAlign = 'center';
            
            // Apply width transform if needed
            if (widthFactor > 1.0) {
                context.save();
                context.translate(canvas.width / 2, canvas.height / 2);
                context.scale(widthFactor, 1);
                context.fillText(text, 0, 0);
                context.restore();
            } else {
                context.fillText(text, canvas.width / 2, canvas.height / 2);
            }
        }
        
        // Create texture from canvas
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        
        // Create sprite material with the texture
        const material = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true
        });
        
        // Create and return the sprite
        const sprite = new THREE.Sprite(material);
        
        // Scale sprite to match aspect ratio
        const aspectRatio = canvas.width / canvas.height;
        sprite.scale.set(aspectRatio, 1, 1);
        
        return sprite;
    }
    
    /**
     * Create a text label for a 3D object
     * 
     * @param {string} text - The text to render
     * @param {Object} options - Configuration options
     * @param {THREE.Object3D} parent - The parent object to attach the text to
     * @param {THREE.Vector3} position - Position relative to parent (default: 0,0,0)
     * @param {number} scale - Text scale (default: 1)
     * @returns {THREE.Sprite} - The created text sprite
     */
    static createLabel(text, options = {}, parent, position = new THREE.Vector3(0, 0, 0), scale = 1) {
        const sprite = this.createTextSprite(text, options);
        sprite.position.copy(position);
        sprite.scale.multiplyScalar(scale);
        
        if (parent) {
            parent.add(sprite);
        }
        
        return sprite;
    }
}

export default TextHelper; 