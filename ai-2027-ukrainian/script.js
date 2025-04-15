document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const links = document.querySelectorAll('nav a, .footer-links a');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            
            if (targetId.startsWith('#') && targetId.length > 1) {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Handle "Read other ending" link
    const readOtherLink = document.querySelector('.read-other');
    if (readOtherLink) {
        readOtherLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Альтернативне закінчення буде доступне незабаром!');
        });
    }
    
    // Mobile navigation toggle (for future implementation)
    // This is a stub for potential mobile menu implementation
    function setupMobileNav() {
        // Future mobile navigation code would go here
    }
    
    // Window resize handler
    window.addEventListener('resize', function() {
        // Adjust layout if needed on resize
    });
    
    // Initialize any animations or transitions
    function initPageAnimations() {
        // Future animation initialization
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach((item, index) => {
            item.style.transitionDelay = (index * 0.1) + 's';
            setTimeout(() => {
                item.classList.add('visible');
            }, 100 * index);
        });
    }
    
    // Call initialization functions
    setupMobileNav();
    initPageAnimations();
}); 