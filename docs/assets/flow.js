/* Homepage flow: tells the header line which part of the page you are in, so its colour
   follows the segment (eCOA teal, device cobalt, Danish coral). Without JavaScript the
   line still fills as you scroll, in the page's own accent. */
(function () {
  var root = document.documentElement;
  var bands = [].slice.call(document.querySelectorAll("[data-band]"));
  function progress() {
    var h = root.scrollHeight - window.innerHeight;
    root.style.setProperty("--p", h > 0 ? Math.min(1, window.scrollY / h).toFixed(4) : 0);
  }
  if (!CSS.supports("animation-timeline: scroll()")) {
    window.addEventListener("scroll", progress, { passive: true });
    progress();
  }
  if (!("IntersectionObserver" in window) || !bands.length) return;
  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) root.setAttribute("data-flow", e.target.getAttribute("data-band"));
      });
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );
  bands.forEach(function (b) { io.observe(b); });
  var top = new IntersectionObserver(function (entries) {
    if (entries[0].isIntersecting) root.removeAttribute("data-flow");
  });
  var hero = document.querySelector(".hero-home");
  if (hero) top.observe(hero);
})();
