/**
 * Birthday Wishes - Golden Hour Celebration
 * Dark mode, Toast, Confetti, Confirm Modal, Scroll Reveal, Typing Effect
 */
(function () {
    'use strict';

    // =============================================
    // Theme (Dark Mode)
    // =============================================
    const theme = {
        get isDark() {
            return document.documentElement.classList.contains('dark');
        },
        init() {
            const saved = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (saved === 'dark' || (!saved && prefersDark)) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },
        toggle() {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        },
    };

    // =============================================
    // Toast Notifications
    // =============================================
    const toast = {
        _container: null,

        init() {
            this._container = document.getElementById('toast-container');
            if (!this._container) {
                this._container = document.createElement('div');
                this._container.id = 'toast-container';
                this._container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
                this._container.setAttribute('aria-live', 'polite');
                document.body.appendChild(this._container);
            }
        },

        _escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        show(message, type, duration) {
            if (!this._container) this.init();
            duration = duration || 3000;

            const config = {
                success: { icon: 'check-circle', border: '#10B981' },
                error: { icon: 'alert-circle', border: '#EF4444' },
                info: { icon: 'info', border: '#3B82F6' },
            };
            const c = config[type] || config.info;

            const svgIcon = c.icon === 'check-circle'
                ? `<svg class="w-5 h-5 text-emerald-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
                : c.icon === 'alert-circle'
                ? `<svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
                : `<svg class="w-5 h-5 text-blue-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

            const id = 'toast-' + Date.now();
            const el = document.createElement('div');
            el.id = id;
            el.className = `toast-enter max-w-sm w-full bg-white dark:bg-[#2D2D3F] rounded-xl shadow-2xl border-l-4 overflow-hidden`;
            el.style.borderLeftColor = c.border;
            el.innerHTML = `
                <div class="flex items-start gap-3 p-4">
                    ${svgIcon}
                    <p class="flex-1 text-sm text-gray-700 dark:text-gray-200">${this._escapeHtml(message)}</p>
                    <button onclick="(function(){var e=document.getElementById('${id}');if(e){e.classList.remove('toast-enter');e.classList.add('toast-exit');setTimeout(function(){if(e.parentNode)e.remove()},300)}})()" class="shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
            `;

            this._container.appendChild(el);

            if (duration > 0) {
                setTimeout(() => {
                    const e = document.getElementById(id);
                    if (e) {
                        e.classList.remove('toast-enter');
                        e.classList.add('toast-exit');
                        setTimeout(() => { if (e.parentNode) e.remove(); }, 300);
                    }
                }, duration);
            }
        },

        success(message, duration) { this.show(message, 'success', duration); },
        error(message, duration) { this.show(message, 'error', duration); },
        info(message, duration) { this.show(message, 'info', duration); },
    };

    // =============================================
    // Confirm Modal
    // =============================================
    const confirmModal = {
        _modal: null,
        _resolve: null,

        init() {
            this._modal = document.getElementById('confirm-modal');
            if (!this._modal) {
                this._modal = document.createElement('div');
                this._modal.id = 'confirm-modal';
                this._modal.className = 'fixed inset-0 z-50 hidden';
                this._modal.setAttribute('role', 'dialog');
                this._modal.setAttribute('aria-modal', 'true');
                this._modal.innerHTML = `
                    <div class="modal-backdrop fixed inset-0 bg-black/40"></div>
                    <div class="fixed inset-0 flex items-center justify-center p-4">
                        <div class="bg-white dark:bg-[#2D2D3F] rounded-2xl shadow-2xl max-w-md w-full p-6 fade-in-up relative" style="max-width: 420px;">
                            <div class="flex items-center gap-3 mb-4">
                                <span class="text-2xl" id="confirm-modal-icon">⚠️</span>
                                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100" id="confirm-modal-title">确认</h3>
                            </div>
                            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-6" id="confirm-modal-message">确定要执行此操作吗？</p>
                            <div class="flex justify-end gap-3">
                                <button id="confirm-modal-cancel" class="px-5 py-2.5 rounded-xl text-sm font-semibold text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">取消</button>
                                <button id="confirm-modal-confirm" class="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] hover:shadow-lg hover:shadow-[#FF6B6B]/30 transition-all">确认</button>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(this._modal);
            }
            this._bindEvents();
        },

        _bindEvents() {
            const cancelBtn = this._modal.querySelector('#confirm-modal-cancel');
            const confirmBtn = this._modal.querySelector('#confirm-modal-confirm');

            const newCancel = cancelBtn.cloneNode(true);
            const newConfirm = confirmBtn.cloneNode(true);
            cancelBtn.parentNode.replaceChild(newCancel, cancelBtn);
            confirmBtn.parentNode.replaceChild(newConfirm, confirmBtn);

            newCancel.addEventListener('click', () => this._close(false));
            newConfirm.addEventListener('click', () => this._close(true));
            this._modal.addEventListener('click', (e) => {
                if (e.target === this._modal || e.target.classList.contains('modal-backdrop')) {
                    this._close(false);
                }
            });
            document.addEventListener('keydown', this._escapeHandler = (e) => {
                if (e.key === 'Escape') this._close(false);
            });
        },

        show(options) {
            if (!this._modal) this.init();
            options = options || {};

            this._modal.querySelector('#confirm-modal-icon').textContent = options.icon || '⚠️';
            this._modal.querySelector('#confirm-modal-title').textContent = options.title || '确认';
            this._modal.querySelector('#confirm-modal-message').textContent = options.message || '确定要执行此操作吗？';

            const confirmBtn = this._modal.querySelector('#confirm-modal-confirm');
            confirmBtn.textContent = options.confirmText || '确认';
            if (options.confirmClass) {
                confirmBtn.className = options.confirmClass;
            } else {
                confirmBtn.className = 'px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] hover:shadow-lg hover:shadow-[#FF6B6B]/30 transition-all';
            }

            this._modal.querySelector('#confirm-modal-cancel').textContent = options.cancelText || '取消';
            this._modal.classList.remove('hidden');

            return new Promise((resolve) => {
                this._resolve = resolve;
            });
        },

        _close(result) {
            this._modal.classList.add('hidden');
            if (this._resolve) {
                this._resolve(result);
                this._resolve = null;
            }
        },
    };

    // =============================================
    // Password Strength Estimator
    // =============================================
    function estimatePasswordStrength(password) {
        if (!password) return { level: 'none', score: 0, label: '无' };

        let score = 0;
        if (password.length >= 6) score += 10;
        if (password.length >= 8) score += 10;
        if (password.length >= 12) score += 10;
        if (password.length >= 16) score += 10;
        if (/[a-z]/.test(password)) score += 10;
        if (/[A-Z]/.test(password)) score += 15;
        if (/[0-9]/.test(password)) score += 15;
        if (/[^a-zA-Z0-9]/.test(password)) score += 20;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 5;
        if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) score += 5;
        if (/[a-zA-Z0-9]/.test(password) && /[^a-zA-Z0-9]/.test(password)) score += 5;

        let level, label;
        if (score < 25) { level = 'weak'; label = '弱'; }
        else if (score < 50) { level = 'fair'; label = '一般'; }
        else if (score < 75) { level = 'good'; label = '良好'; }
        else { level = 'strong'; label = '强'; }

        return { level, score: Math.min(score, 100), label };
    }

    // =============================================
    // Confetti Celebration (canvas-confetti wrapper)
    // =============================================
    const celebrate = {
        burst() {
            if (typeof confetti !== 'function' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            const defaults = {
                particleCount: 120, spread: 70, origin: { y: 0.6 },
                colors: ['#FF6B6B', '#FFD700', '#FFA07A', '#FF4D6D', '#3EC1D3', '#6C5CE7', '#FFD93D'],
            };
            confetti({ ...defaults });
            setTimeout(() => confetti({ ...defaults, particleCount: 60, spread: 100, angle: 60 }), 150);
            setTimeout(() => confetti({ ...defaults, particleCount: 60, spread: 100, angle: 120 }), 300);
        },
        fireworks() {
            if (typeof confetti !== 'function' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            const end = Date.now() + 2000;
            const colors = ['#FF6B6B', '#FFD700', '#FFA07A', '#FF4D6D', '#3EC1D3'];
            (function frame() {
                confetti({ particleCount: 4, angle: 60, spread: 55, origin: { x: 0, y: 0.7 }, colors });
                confetti({ particleCount: 4, angle: 120, spread: 55, origin: { x: 1, y: 0.7 }, colors });
                if (Date.now() < end) requestAnimationFrame(frame);
            })();
        },
        long() {
            if (typeof confetti !== 'function' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            const end = Date.now() + 3000;
            const colors = ['#FF6B6B', '#FFD700', '#FFA07A', '#FF4D6D', '#3EC1D3'];
            (function frame() {
                confetti({ particleCount: 6, angle: 90, spread: 80, origin: { y: 0.5 }, colors });
                if (Date.now() < end) requestAnimationFrame(frame);
            })();
        },
        once() {
            if (!sessionStorage.getItem('confetti-shown')) {
                sessionStorage.setItem('confetti-shown', 'true');
                setTimeout(() => this.burst(), 500);
            }
        },
    };

    // =============================================
    // Scroll Reveal (IntersectionObserver)
    // =============================================
    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const delay = parseInt(el.dataset.revealDelay) || 0;
                    setTimeout(() => {
                        el.classList.add('slide-up-stagger');
                        el.style.opacity = '1';
                    }, delay);
                    observer.unobserve(el);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

        document.querySelectorAll('[data-reveal]').forEach((el) => {
            el.style.opacity = '0';
            observer.observe(el);
        });
    }

    // =============================================
    // Typing Effect
    // =============================================
    function typeText(element, text, speed, callback) {
        if (!element) return;
        speed = speed || 50;
        let i = 0;
        element.textContent = '';
        element.classList.add('typing-cursor');

        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed + Math.random() * 40);
            } else {
                element.classList.remove('typing-cursor');
                if (callback) callback();
            }
        }
        type();
    }

    // =============================================
    // Feature Card Hover
    // =============================================
    function initFeatureCards() {
        document.querySelectorAll('.card-hover').forEach((card) => {
            card.addEventListener('mouseenter', function () {
                const icon = this.querySelector('.feature-icon');
                if (icon) icon.style.transform = 'scale(1.15)';
            });
            card.addEventListener('mouseleave', function () {
                const icon = this.querySelector('.feature-icon');
                if (icon) icon.style.transform = 'scale(1)';
            });
        });
    }

    // =============================================
    // Init On DOMContentLoaded
    // =============================================
    document.addEventListener('DOMContentLoaded', function () {
        theme.init();
        toast.init();
        confirmModal.init();
        initFeatureCards();
        initScrollReveal();

        // Auto-trigger typing effect for elements with data-type-text
        document.querySelectorAll('[data-type-text]').forEach((el) => {
            const text = el.dataset.typeText;
            const speed = parseInt(el.dataset.typeSpeed) || 50;
            typeText(el, text, speed);
        });

        // Auto-trigger confetti
        document.querySelectorAll('[data-celebrate]').forEach((el) => {
            const type = el.dataset.celebrate || 'burst';
            if (celebrate[type]) celebrate[type]();
        });

        // Dashboard celebration (once per session)
        if (document.querySelector('[data-celebrate-once]')) {
            celebrate.once();
        }

        // Expose to window
        window.theme = theme;
        window.toast = toast;
        window.confirmModal = confirmModal;
        window.estimatePasswordStrength = estimatePasswordStrength;
        window.celebrate = celebrate;
        window.typeText = typeText;
    });
})();
