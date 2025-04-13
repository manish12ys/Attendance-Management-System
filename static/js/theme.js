// Theme Switcher for Attendance Management System

document.addEventListener('DOMContentLoaded', function() {
    // Apply saved theme immediately to prevent flash of wrong theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    console.log('Theme initialized:', savedTheme);

    // Theme toggle buttons (could be multiple in the page)
    const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');

    if (themeToggleBtns.length > 0) {
        // Update all button icons based on current theme
        themeToggleBtns.forEach(btn => {
            updateThemeIcon(btn, savedTheme);
        });

        // Add click event to all theme toggle buttons
        themeToggleBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';

                // Set the new theme
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                console.log('Theme changed to:', newTheme);

                // Update all button icons
                themeToggleBtns.forEach(btn => {
                    updateThemeIcon(btn, newTheme);
                });

                // Dispatch a custom event for other scripts that might need to react to theme changes
                document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
            });
        });
    }

    // Function to update theme toggle icon
    function updateThemeIcon(button, theme) {
        // Clear existing icons
        button.innerHTML = '';

        // Create appropriate icon based on theme
        const icon = document.createElement('i');

        if (theme === 'light') {
            icon.className = 'fas fa-moon';
            button.setAttribute('title', 'Switch to Dark Mode');
            button.setAttribute('aria-label', 'Switch to Dark Mode');
        } else {
            icon.className = 'fas fa-sun';
            button.setAttribute('title', 'Switch to Light Mode');
            button.setAttribute('aria-label', 'Switch to Light Mode');
        }

        button.appendChild(icon);
    }

    // Function to get system preference for dark/light mode
    function getSystemThemePreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Listen for system theme preference changes
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', e => {
            // Only change theme if user hasn't explicitly set a preference
            if (!localStorage.getItem('theme')) {
                const newTheme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', newTheme);

                // Update all button icons
                themeToggleBtns.forEach(btn => {
                    updateThemeIcon(btn, newTheme);
                });
            }
        });
    }
});
