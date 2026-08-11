document.addEventListener('DOMContentLoaded', () => {
  const intro = document.getElementById('intro-screen');
  const video = document.getElementById('intro-video');
  const site = document.getElementById('site-wrapper');

  if (!intro || !video || !site) return;

  // If intro already played in this browser session
  if (sessionStorage.getItem('mynaroda_intro_seen') === '1') {
    intro.remove();
    site.classList.add('show');
    return;
  }

  // Play intro (it's muted in HTML to guarantee autoplay works on all browsers)
  video.play().catch((err) => {
    console.warn("Autoplay blocked:", err);
  });

  // If user clicks anywhere during the video, try to unmute it to play audio
  document.addEventListener('click', () => {
    video.muted = false;
  }, { once: true });

  video.addEventListener('ended', () => {
    sessionStorage.setItem('mynaroda_intro_seen', '1');
    intro.classList.add('hide');
    setTimeout(() => {
      intro.remove();
      site.classList.add('show');
    }, 1000);
  });
});
