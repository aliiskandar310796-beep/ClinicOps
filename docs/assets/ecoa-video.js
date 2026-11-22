(function () {
  var v = document.getElementById("ecoa-video");
  if (!v) return;
  var links = Array.prototype.slice.call(document.querySelectorAll(".chapters a.go"));
  var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  function seek(t) {
    function go() {
      v.currentTime = t;
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    }
    if (v.readyState > 0) go();
    else {
      v.addEventListener("loadedmetadata", go, { once: true });
      v.load();
    }
  }
  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      v.scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "center" });
      seek(parseFloat(a.getAttribute("data-t")));
    });
  });
  v.addEventListener("timeupdate", function () {
    var cur = -1;
    links.forEach(function (a, i) {
      if (v.currentTime >= parseFloat(a.getAttribute("data-t")) - 0.2) cur = i;
    });
    links.forEach(function (a, i) {
      a.parentNode.classList.toggle("now", i === cur);
    });
  });
})();
