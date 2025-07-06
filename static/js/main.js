// Main JavaScript for Privacy Platform
(function() {
    'use strict';

    // DOM Content Loaded Event
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    // Initialize the application
    function initializeApp() {
        initializeTooltips();
        initializeFormValidation();
        initializeProgressBars();
        initializeCounters();
        initializeSmoothScrolling();
        initializeCardAnimations();
        initializeAssessmentFeatures();
        initializeNavigation();
        handleFlashMessages();
    }

    // Initialize Bootstrap tooltips
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Enhanced form validation
    function initializeFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.prototype.slice.call(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Focus on first invalid field
                    const firstInvalidField = form.querySelector(':invalid');
                    if (firstInvalidField) {
                        firstInvalidField.focus();
                    }
                }
                form.classList.add('was-validated');
            }, false);
        });

        // Real-time validation for specific fields
        initializeRealTimeValidation();
    }

    // Real-time form validation
    function initializeRealTimeValidation() {
        // Email validation
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateEmail(this);
            });
        });

        // Password strength validation
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                if (this.name === 'password') {
                    validatePasswordStrength(this);
                }
            });
        });

        // Username availability check (simulated)
        const usernameInput = document.querySelector('input[name="username"]');
        if (usernameInput) {
            let usernameTimeout;
            usernameInput.addEventListener('input', function() {
                clearTimeout(usernameTimeout);
                usernameTimeout = setTimeout(() => {
                    checkUsernameAvailability(this);
                }, 500);
            });
        }
    }

    // Email validation
    function validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(input.value);
        
        updateFieldValidation(input, isValid, 'Please enter a valid email address');
    }

    // Password strength validation
    function validatePasswordStrength(input) {
        const password = input.value;
        const minLength = 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        let strength = 0;
        let message = '';

        if (password.length >= minLength) strength++;
        if (hasUpperCase) strength++;
        if (hasLowerCase) strength++;
        if (hasNumbers) strength++;
        if (hasSpecialChar) strength++;

        // Create or update password strength indicator
        let strengthIndicator = input.parentNode.querySelector('.password-strength');
        if (!strengthIndicator) {
            strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength mt-2';
            input.parentNode.appendChild(strengthIndicator);
        }

        if (password.length === 0) {
            strengthIndicator.innerHTML = '';
            return;
        }

        if (strength < 3) {
            message = 'Weak password';
            strengthIndicator.className = 'password-strength mt-2 text-danger';
        } else if (strength < 4) {
            message = 'Medium password';
            strengthIndicator.className = 'password-strength mt-2 text-warning';
        } else {
            message = 'Strong password';
            strengthIndicator.className = 'password-strength mt-2 text-success';
        }

        strengthIndicator.innerHTML = `
            <small>
                <i class="fas fa-shield-alt me-1"></i>${message}
                <div class="progress mt-1" style="height: 4px;">
                    <div class="progress-bar" style="width: ${(strength / 5) * 100}%"></div>
                </div>
            </small>
        `;
    }

    // Username availability check (simulated)
    function checkUsernameAvailability(input) {
        if (input.value.length < 4) return;

        // Simulate API call delay
        const indicator = getOrCreateIndicator(input, 'username-check');
        indicator.innerHTML = '<small class="text-muted"><i class="fas fa-spinner fa-spin me-1"></i>Checking availability...</small>';

        setTimeout(() => {
            // Simulate some usernames as taken
            const takenUsernames = ['admin', 'test', 'user', 'demo'];
            const isAvailable = !takenUsernames.includes(input.value.toLowerCase());
            
            if (isAvailable) {
                indicator.innerHTML = '<small class="text-success"><i class="fas fa-check me-1"></i>Username available</small>';
            } else {
                indicator.innerHTML = '<small class="text-danger"><i class="fas fa-times me-1"></i>Username not available</small>';
            }
        }, 1000);
    }

    // Update field validation state
    function updateFieldValidation(input, isValid, message) {
        const feedback = input.parentNode.querySelector('.invalid-feedback') || 
                        input.parentNode.querySelector('.valid-feedback');
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            if (feedback) {
                feedback.textContent = 'Looks good!';
                feedback.className = 'valid-feedback';
            }
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            if (feedback) {
                feedback.textContent = message;
                feedback.className = 'invalid-feedback';
            }
        }
    }

    // Get or create indicator element
    function getOrCreateIndicator(input, className) {
        let indicator = input.parentNode.querySelector(`.${className}`);
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = className;
            input.parentNode.appendChild(indicator);
        }
        return indicator;
    }

    // Initialize progress bars with animation
    function initializeProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        const observerCallback = function(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const width = progressBar.style.width || progressBar.getAttribute('aria-valuenow') + '%';
                    
                    progressBar.style.width = '0%';
                    setTimeout(() => {
                        progressBar.style.transition = 'width 1.5s ease-in-out';
                        progressBar.style.width = width;
                    }, 100);
                    
                    observer.unobserve(progressBar);
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, {
            threshold: 0.5
        });

        progressBars.forEach(bar => {
            observer.observe(bar);
        });
    }

    // Initialize counters animation
    function initializeCounters() {
        const counters = document.querySelectorAll('.counter');
        
        const observerCallback = function(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target'));
                    const duration = 2000; // 2 seconds
                    const increment = target / (duration / 16); // 60fps
                    
                    let current = 0;
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            counter.textContent = target;
                            clearInterval(timer);
                        } else {
                            counter.textContent = Math.floor(current);
                        }
                    }, 16);
                    
                    observer.unobserve(counter);
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, {
            threshold: 0.5
        });

        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    // Smooth scrolling for anchor links
    function initializeSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Card hover animations
    function initializeCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.transition = 'all 0.3s ease';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // Assessment specific features
    function initializeAssessmentFeatures() {
        initializeAssessmentProgress();
        initializeQuestionNavigation();
        initializeAssessmentTimer();
    }

    // Assessment progress tracking
    function initializeAssessmentProgress() {
        const assessmentForm = document.getElementById('assessmentForm');
        if (!assessmentForm) return;

        const radioInputs = assessmentForm.querySelectorAll('input[type="radio"]');
        const progressContainer = document.createElement('div');
        progressContainer.className = 'assessment-progress sticky-top bg-light p-3 shadow-sm border';
        progressContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-dark fw-bold">Assessment Progress</small>
                <small class="text-dark"><span class="progress-text fw-bold">0% Complete</span></small>
            </div>
            <div class="progress mt-2" style="height: 10px;">
                <div class="progress-bar bg-primary" role="progressbar" style="width: 0%"></div>
            </div>
        `;

        assessmentForm.insertBefore(progressContainer, assessmentForm.firstChild);

        const progressBar = progressContainer.querySelector('.progress-bar');
        const progressText = progressContainer.querySelector('.progress-text');

        function updateProgress() {
            const totalQuestions = new Set();
            const answeredQuestions = new Set();

            radioInputs.forEach(input => {
                const questionId = input.name.replace('question_', '');
                totalQuestions.add(questionId);

                if (input.checked) {
                    answeredQuestions.add(questionId);
                }
            });

            const progress = (answeredQuestions.size / totalQuestions.size) * 100;
            progressBar.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '% Complete';

            // Update submit button
            const submitBtn = assessmentForm.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                if (progress === 100) {
                    submitBtn.classList.remove('btn-primary');
                    submitBtn.classList.add('btn-success');
                    submitBtn.textContent = submitBtn.textContent.replace('Calculate', '✓ Calculate');
                } else {
                    submitBtn.classList.remove('btn-success');
                    submitBtn.classList.add('btn-primary');
                    submitBtn.textContent = submitBtn.textContent.replace('✓ ', '');
                }
            }
        }

        radioInputs.forEach(input => {
            input.addEventListener('change', updateProgress);
        });

        updateProgress();
    }

    // Question navigation
    function initializeQuestionNavigation() {
        const questionSections = document.querySelectorAll('.card');
        
        questionSections.forEach((section, index) => {
            const header = section.querySelector('.card-header');
            if (header) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    section.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                });
            }
        });
    }

    // Assessment timer
    function initializeAssessmentTimer() {
        const assessmentForm = document.getElementById('assessmentForm');
        if (!assessmentForm) return;

        const startTime = Date.now();
        const timerContainer = document.createElement('div');
        timerContainer.className = 'assessment-timer text-center text-muted mb-3';
        timerContainer.innerHTML = '<small><i class="fas fa-clock me-1"></i>Time elapsed: <span class="timer-text">00:00</span></small>';

        assessmentForm.appendChild(timerContainer);

        const timerText = timerContainer.querySelector('.timer-text');

        setInterval(() => {
            const elapsed = Date.now() - startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            timerText.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    // Navigation enhancements
    function initializeNavigation() {
        // Active link highlighting
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Mobile menu improvements
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse && navbarCollapse.classList.contains('show')) {
                        bsCollapse.hide();
                    }
                }
            });

            // Close mobile menu when clicking on a link
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse && navbarCollapse.classList.contains('show')) {
                        bsCollapse.hide();
                    }
                });
            });
        }
    }

    // Flash messages handling
    function handleFlashMessages() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        
        alerts.forEach(alert => {
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    // Utility functions
    window.PrivacyPlatform = {
        // Show loading state
        showLoading: function(element, text = 'Loading...') {
            element.disabled = true;
            element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
        },

        // Hide loading state
        hideLoading: function(element, originalText) {
            element.disabled = false;
            element.innerHTML = originalText;
        },

        // Show toast notification
        showToast: function(message, type = 'info') {
            const toastContainer = document.getElementById('toast-container') || createToastContainer();
            
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${getToastIcon(type)} me-2"></i>${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

            toastContainer.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();

            // Remove toast element after hiding
            toast.addEventListener('hidden.bs.toast', function() {
                this.remove();
            });
        },

        // Confirm dialog
        confirm: function(message, callback) {
            if (confirm(message)) {
                callback();
            }
        },

        // Format currency
        formatCurrency: function(amount, currency = 'USD') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },

        // Copy to clipboard
        copyToClipboard: function(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard!', 'success');
            }).catch(() => {
                this.showToast('Failed to copy to clipboard', 'danger');
            });
        }
    };

    // Helper functions
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    function getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Expose utility functions globally
    window.showLoading = window.PrivacyPlatform.showLoading;
    window.hideLoading = window.PrivacyPlatform.hideLoading;
    window.showToast = window.PrivacyPlatform.showToast;

})();

// Additional feature: Auto-save form data
(function() {
    'use strict';

    const STORAGE_PREFIX = 'privacy_platform_';
    const SAVE_INTERVAL = 30000; // 30 seconds

    // Auto-save form data
    function initializeAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');
        
        forms.forEach(form => {
            const formId = form.getAttribute('data-autosave');
            const storageKey = STORAGE_PREFIX + formId;
            
            // Load saved data
            loadFormData(form, storageKey);
            
            // Save data on change
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    saveFormData(form, storageKey);
                });
            });
            
            // Periodic save
            setInterval(() => {
                saveFormData(form, storageKey);
            }, SAVE_INTERVAL);
            
            // Clear data on successful submit
            form.addEventListener('submit', () => {
                clearFormData(storageKey);
            });
        });
    }

    function saveFormData(form, storageKey) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        try {
            localStorage.setItem(storageKey, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save form data:', e);
        }
    }

    function loadFormData(form, storageKey) {
        try {
            const savedData = localStorage.getItem(storageKey);
            if (!savedData) return;
            
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'password') {
                    if (input.type === 'checkbox' || input.type === 'radio') {
                        input.checked = input.value === data[key];
                    } else {
                        input.value = data[key];
                    }
                }
            });
            
            // Show notification
            showToast('Form data restored from previous session', 'info');
        } catch (e) {
            console.warn('Failed to load form data:', e);
        }
    }

    function clearFormData(storageKey) {
        try {
            localStorage.removeItem(storageKey);
        } catch (e) {
            console.warn('Failed to clear form data:', e);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAutoSave);
    } else {
        initializeAutoSave();
    }

})();
