(function () {
  var mount = document.getElementById('giscus-container');
  if (!mount) return;

  var cfg = window.GISCUS_CONFIG || {};
  var notReady = !cfg.repo || cfg.repo.indexOf('USERNAME/REPOSITORY') !== -1 || !cfg.repoId || !cfg.categoryId;

  if (notReady) {
    mount.innerHTML =
      '<div class="empty-state">' +
      '아직 댓글창이 연결되지 않았습니다.<br>' +
      '<code style="font-family:var(--font-mono)">assets/js/giscus-config.js</code> 파일에 ' +
      'giscus 설정값을 입력하면 이 자리에 댓글·추천(👍) 창이 표시됩니다.' +
      '</div>';
    return;
  }

  var script = document.createElement('script');
  script.src = 'https://giscus.app/client.js';
  script.setAttribute('data-repo', cfg.repo);
  script.setAttribute('data-repo-id', cfg.repoId);
  script.setAttribute('data-category', cfg.category);
  script.setAttribute('data-category-id', cfg.categoryId);
  script.setAttribute('data-mapping', cfg.mapping || 'pathname');
  script.setAttribute('data-reactions-enabled', cfg.reactionsEnabled || '1');
  script.setAttribute('data-emit-metadata', cfg.emitMetadata || '0');
  script.setAttribute('data-input-position', cfg.inputPosition || 'top');
  script.setAttribute('data-theme', cfg.theme || 'light');
  script.setAttribute('data-lang', cfg.lang || 'ko');
  script.crossOrigin = 'anonymous';
  script.async = true;
  mount.appendChild(script);
})();
