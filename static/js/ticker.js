document.addEventListener('DOMContentLoaded', function() {
    const ticker = document.querySelector('.books_sticker');
    if (!ticker) return;

    const items = ticker.querySelectorAll('li');
    if (items.length <= 1) return;

    let currentIndex = 0;
    const itemWidth = items[0].offsetWidth;
    const containerWidth = ticker.offsetWidth;
    const totalWidth = items.length * itemWidth;

    function animateTicker() {
        currentIndex++;
        if (currentIndex >= items.length) {
            currentIndex = 0;
        }

        const offset = -currentIndex * itemWidth;
        ticker.style.transform = `translateX(${offset}px)`;
    }

    // Start the animation
    setInterval(animateTicker, 3000);
}); 