document.addEventListener('DOMContentLoaded', () => {
    // Smooth Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');

        question.addEventListener('click', () => {
            answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Animations on Scroll
    const observers = document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            }
        });
    });

    observers.forEach(observee => observer.observe(observee));

    // Styling for Animations
    const style = document.createElement('style');
    style.innerHTML = ".in-view {transform: translateY(0); opacity: 1; transition: all 0.5s ease;}";
    document.head.appendChild(style);

    // Set initial hidden animation states
    observers.forEach(elem => {
        elem.style.transform = 'translateY(50px)';
        elem.style.opacity = '0';
    });
});
