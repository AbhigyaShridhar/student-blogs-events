function navSlide() {
	const burger = document.querySelector("#top .burger");
	const nav = document.querySelector('#top .nav-links');
	const navLinks = document.querySelectorAll('#top .nav-links li')

	burger.addEventListener('click', () => {
		nav.classList.toggle('nav-active');

		//animation
		navLinks.forEach((link, index) => {
		if (link.style.animation) {
			link.style.animation = "";
		} else {
			link.style.animation = `navLinkFade 0.5s ease forwards ${index/7 + 1}s`;
		}
	});

		burger.classList.toggle('toggle');

	});
}

navSlide();