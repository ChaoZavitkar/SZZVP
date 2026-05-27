/**
 * NerdMatch Tinder-Style Swipe
 * Handle card swiping and animations
 */

class TinderSwipe {
    constructor() {
        this.card = document.querySelector('.tinder-card');
        this.skipBtn = document.querySelector('.btn-skip');
        this.likeBtn = document.querySelector('.btn-like');
        this.filterToggle = document.querySelector('.filter-toggle-btn');
        this.filterSection = document.querySelector('.filter-section');

        this.startX = 0;
        this.startY = 0;
        this.currentX = 0;
        this.isDragging = false;

        this.init();
    }

    init() {
        if (!this.card) return;

        // Reset card state
        this.card.style.transform = '';
        this.card.style.opacity = '1';
        this.card.classList.remove('swipe-left', 'swipe-right', 'dragging');

        // Touch events
        this.card.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.card.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.card.addEventListener('touchend', (e) => this.handleTouchEnd(e));

        // Mouse events
        this.card.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleMouseUp(e));

        // Button clicks
        if (this.skipBtn) {
            this.skipBtn.addEventListener('click', () => this.swipeLeft());
        }
        if (this.likeBtn) {
            this.likeBtn.addEventListener('click', () => this.swipeRight());
        }

        // Filter toggle
        if (this.filterToggle) {
            this.filterToggle.addEventListener('click', () => this.toggleFilter());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.swipeLeft();
            if (e.key === 'ArrowRight') this.swipeRight();
            if (e.key === 'Escape') this.closeFilter();
        });
    }

    handleTouchStart(e) {
        this.isDragging = true;
        this.startX = e.touches[0].clientX;
        this.startY = e.touches[0].clientY;
        this.card.classList.add('dragging');
    }

    handleTouchMove(e) {
        if (!this.isDragging) return;
        this.currentX = e.touches[0].clientX - this.startX;
        this.applyDragTransform();
    }

    handleTouchEnd(e) {
        this.isDragging = false;
        this.handleDragEnd();
        this.card.classList.remove('dragging');
    }

    handleMouseDown(e) {
        this.isDragging = true;
        this.startX = e.clientX;
        this.startY = e.clientY;
        this.card.classList.add('dragging');
    }

    handleMouseMove(e) {
        if (!this.isDragging) return;
        this.currentX = e.clientX - this.startX;
        this.applyDragTransform();
    }

    handleMouseUp(e) {
        this.isDragging = false;
        this.handleDragEnd();
        this.card.classList.remove('dragging');
    }

    applyDragTransform() {
        const rotation = (this.currentX / window.innerWidth) * 20;
        const opacity = 1 - Math.abs(this.currentX) / window.innerWidth;

        this.card.style.transform = `translateX(${this.currentX}px) rotate(${rotation}deg)`;
        this.card.style.opacity = Math.max(opacity, 0.5);
    }

    handleDragEnd() {
        const threshold = window.innerWidth * 0.3;

        if (this.currentX > threshold) {
            this.swipeRight();
        } else if (this.currentX < -threshold) {
            this.swipeLeft();
        } else {
            // Return to original position with animation
            this.card.style.transition = 'transform 0.2s ease-out, opacity 0.2s ease-out';
            this.card.style.transform = '';
            this.card.style.opacity = '1';
            setTimeout(() => {
                this.card.style.transition = '';
            }, 200);
            this.currentX = 0;
        }
    }

    swipeLeft() {
        if (this.card.classList.contains('swipe-left') ||
            this.card.classList.contains('swipe-right')) {
            return; // Already swiping
        }
        this.card.classList.add('swipe-left');
        this.showLoadingState();
        setTimeout(() => {
            const skipForm = document.getElementById('skip-form');
            if (skipForm) {
                skipForm.submit();
            } else {
                console.warn('Skip form not found!');
            }
        }, 300);
    }

    swipeRight() {
        if (this.card.classList.contains('swipe-left') ||
            this.card.classList.contains('swipe-right')) {
            return; // Already swiping
        }
        this.card.classList.add('swipe-right');
        this.showLoadingState();
        setTimeout(() => {
            const likeForm = document.getElementById('like-form');
            if (likeForm) {
                likeForm.submit();
            } else {
                console.warn('Like form not found!');
            }
        }, 300);
    }

    showLoadingState() {
        // Add loading animation while page reloads
        this.card.style.opacity = '0.5';
    }

    toggleFilter() {
        if (this.filterSection) {
            this.filterSection.classList.toggle('open');
            this.filterToggle.textContent = this.filterSection.classList.contains('open')
                ? '⬇️ Skrýt filtr'
                : '⬆️ Zobrazit filtr';
        }
    }

    closeFilter() {
        if (this.filterSection && this.filterSection.classList.contains('open')) {
            this.filterSection.classList.remove('open');
            if (this.filterToggle) {
                this.filterToggle.textContent = '⬆️ Zobrazit filtr';
            }
        }
    }

    showMatchNotification(partnerName) {
        const notification = document.querySelector('.match-notification');
        if (!notification) return;

        notification.innerHTML = `
            <div class="match-notification-emoji">💘</div>
            <div class="match-notification-title">JE TO MATCH!</div>
            <div class="match-notification-text">Ty a <strong>${partnerName}</strong> si vzájemně padnete!</div>
            <div style="margin-top: 20px; font-size: 14px;">🎉 Pojďte si psát zprávy! 🎉</div>
        `;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.tinderSwipe = new TinderSwipe();
});
