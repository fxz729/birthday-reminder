/**
 * Birthday Wishes - Main JavaScript
 * Dark mode, Toast notifications, Confirm modal, Password strength
 */

(function () {
    'use strict';

    // =====================================
    // Dark Mode Toggle
    // =====================================
    const theme = {
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
        get isDark() {
            return document.documentElement.classList.contains('dark');
        },
    };

    // =====================================
    // Toast Manager
    // =====================================
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

        /**
         * Show a toast notification
         * @param {string} message - The message to display
         * @param {'success'|'error'|'info'} type - Toast type
         * @param {number} duration - Auto-dismiss duration in ms (default 3000)
         */
        show(message, type, duration) {
            if (!this._container) this.init();
            duration = duration || 3000;

            const icons = {
                success: '✅',
                error: '❌',
                info: 'ℹ️',
            };

            const colors = {
                success: 'bg-white dark:bg-[#2D2D3F] border-l-4 border-[#7EBF8E] text-gray-800 dark:text-gray-100',
                error: 'bg-white dark:bg-[#2D2D3F] border-l-4 border-[#FF6B6B] text-gray-800 dark:text-gray-100',
                info: 'bg-white dark:bg-[#2D2D3F] border-l-4 border-[#7EC8E3] text-gray-800 dark:text-gray-100',
            };

            const el = document.createElement('div');
            el.className = `toast-enter flex items-center gap-3 px-5 py-3 rounded-xl shadow-lg ${colors[type] || colors.info} min-w-[280px] max-w-[420px]`;
            el.innerHTML = `
                <span class="text-lg flex-shrink-0">${icons[type] || icons.info}</span>
                <span class="text-sm font-medium flex-1">${this._escapeHtml(message)}</span>
                <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 flex-shrink-0 text-lg leading-none" onclick="this.parentElement.remove()">&times;</button>
            `;

            this._container.appendChild(el);

            if (duration > 0) {
                setTimeout(() => {
                    el.classList.remove('toast-enter');
                    el.classList.add('toast-exit');
                    setTimeout(() => el.remove(), 300);
                }, duration);
            }
        },

        success(message, duration) { this.show(message, 'success', duration); },
        error(message, duration) { this.show(message, 'error', duration); },
        info(message, duration) { this.show(message, 'info', duration); },

        _escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
    };

    // =====================================
    // Confirm Modal
    // =====================================
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
                                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 font-['Quicksand']" id="confirm-modal-title">确认</h3>
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

            // Remove old listeners by cloning
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

        /**
         * Show a confirmation dialog
         * @param {Object} options
         * @param {string} options.title - Modal title
         * @param {string} options.message - Modal message
         * @param {string} [options.icon] - Emoji icon
         * @param {string} [options.confirmText] - Confirm button text
         * @param {string} [options.cancelText] - Cancel button text
         * @param {string} [options.confirmClass] - Additional classes for confirm btn
         * @returns {Promise<boolean>}
         */
        show(options) {
            if (!this._modal) this.init();
            options = options || {};

            this._modal.querySelector('#confirm-modal-icon').textContent = options.icon || '⚠️';
            this._modal.querySelector('#confirm-modal-title').textContent = options.title || '确认';
            this._modal.querySelector('#confirm-modal-message').textContent = options.message || '确定要执行此操作吗？';

            const confirmBtn = this._modal.querySelector('#confirm-modal-confirm');
            confirmBtn.textContent = options.confirmText || '确认';
            if (options.confirmClass) {
                confirmBtn.className = `px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all ${options.confirmClass}`;
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

    // =====================================
    // Password Strength Estimator
    // =====================================
    function estimatePasswordStrength(password) {
        if (!password) return { level: 'none', score: 0, label: '无' };

        let score = 0;

        // Length scoring
        if (password.length >= 6) score += 10;
        if (password.length >= 8) score += 10;
        if (password.length >= 12) score += 10;
        if (password.length >= 16) score += 10;

        // Character variety
        if (/[a-z]/.test(password)) score += 10;
        if (/[A-Z]/.test(password)) score += 15;
        if (/[0-9]/.test(password)) score += 15;
        if (/[^a-zA-Z0-9]/.test(password)) score += 20;

        // Additional patterns
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 5;
        if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) score += 5;
        if (/[a-zA-Z0-9]/.test(password) && /[^a-zA-Z0-9]/.test(password)) score += 5;

        let level, label;
        if (score < 25) {
            level = 'weak';
            label = '弱';
        } else if (score < 50) {
            level = 'fair';
            label = '一般';
        } else if (score < 75) {
            level = 'good';
            label = '良好';
        } else {
            level = 'strong';
            label = '强';
        }

        return { level, score: Math.min(score, 100), label };
    }

    // =====================================
    // Feature Card Hover (Alpine.js compatible)
    // =====================================
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

    // =====================================
    // Init On DOMContentLoaded
    // =====================================
    document.addEventListener('DOMContentLoaded', function () {
        theme.init();

        // Initialize toast and confirm modal
        toast.init();
        confirmModal.init();

        // Expose to window
        window.theme = theme;
        window.toast = toast;
        window.confirmModal = confirmModal;
        window.estimatePasswordStrength = estimatePasswordStrength;

        // Feature card icons
        initFeatureCards();
    });
})();
