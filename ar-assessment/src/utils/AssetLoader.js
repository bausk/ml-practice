import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { TextureLoader } from 'three';

/**
 * Utility class for loading various assets with progress tracking
 */
export class AssetLoader {
    constructor() {
        this.fontLoader = new FontLoader();
        this.gltfLoader = new GLTFLoader();
        this.textureLoader = new TextureLoader();
        
        this.loadingManager = {
            items: {},
            itemsLoaded: 0,
            itemsTotal: 0,
            onProgress: null
        };
    }
    
    /**
     * Set progress callback
     * @param {Function} callback - Progress callback with percent loaded
     */
    setProgressCallback(callback) {
        this.loadingManager.onProgress = callback;
    }
    
    /**
     * Update progress
     * @param {string} url - Asset URL
     * @param {boolean} loaded - Whether the asset has loaded
     */
    updateProgress(url, loaded) {
        if (loaded) {
            this.loadingManager.itemsLoaded++;
        } else if (!this.loadingManager.items[url]) {
            this.loadingManager.items[url] = true;
            this.loadingManager.itemsTotal++;
        }
        
        const progress = this.loadingManager.itemsTotal === 0 
            ? 1 
            : this.loadingManager.itemsLoaded / this.loadingManager.itemsTotal;
            
        if (this.loadingManager.onProgress) {
            this.loadingManager.onProgress(progress);
        }
    }
    
    /**
     * Load a font
     * @param {string} url - Font URL
     * @returns {Promise} - Promise resolving to the loaded font
     */
    loadFont(url) {
        this.updateProgress(url, false);
        
        return new Promise((resolve, reject) => {
            this.fontLoader.load(
                url,
                (font) => {
                    this.updateProgress(url, true);
                    resolve(font);
                },
                null,
                (error) => {
                    console.error(`Error loading font ${url}:`, error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Load a GLTF model
     * @param {string} url - Model URL
     * @returns {Promise} - Promise resolving to the loaded model
     */
    loadModel(url) {
        this.updateProgress(url, false);
        
        return new Promise((resolve, reject) => {
            this.gltfLoader.load(
                url,
                (gltf) => {
                    this.updateProgress(url, true);
                    resolve(gltf);
                },
                null,
                (error) => {
                    console.error(`Error loading model ${url}:`, error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Load a texture
     * @param {string} url - Texture URL
     * @returns {Promise} - Promise resolving to the loaded texture
     */
    loadTexture(url) {
        this.updateProgress(url, false);
        
        return new Promise((resolve, reject) => {
            this.textureLoader.load(
                url,
                (texture) => {
                    this.updateProgress(url, true);
                    resolve(texture);
                },
                null,
                (error) => {
                    console.error(`Error loading texture ${url}:`, error);
                    reject(error);
                }
            );
        });
    }
}

// Export a singleton instance
export default new AssetLoader(); 