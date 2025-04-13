// Check the theme toggle functionality
console.log('Current theme:', document.documentElement.getAttribute('data-theme'));

// Get the theme toggle button
const themeToggleBtn = document.querySelector('.theme-toggle-btn');
if (themeToggleBtn) {
    console.log('Theme toggle button found');
    
    // Simulate a click on the theme toggle button
    themeToggleBtn.click();
    
    // Check the theme after clicking
    console.log('Theme after click:', document.documentElement.getAttribute('data-theme'));
    
    // Click again to revert
    themeToggleBtn.click();
    
    // Check the theme after clicking again
    console.log('Theme after second click:', document.documentElement.getAttribute('data-theme'));
} else {
    console.log('Theme toggle button not found');
}
