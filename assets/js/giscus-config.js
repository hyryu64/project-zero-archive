/**
 * giscus 댓글 설정 파일
 * -------------------------------------------------------------
 * 이 파일 한 곳만 수정하면 모든 우수작 상세 페이지의 댓글창에 반영됩니다.
 *
 * 값을 채우는 방법:
 *  1. GitHub 저장소(repository)를 만들고, 저장소 Settings → General →
 *     Features 에서 "Discussions" 기능을 켭니다.
 *  2. https://giscus.app 에 접속해 저장소 이름을 입력하고 안내에 따라
 *     giscus 앱을 설치합니다.
 *  3. giscus.app 페이지 하단에 생성되는 값들을 아래에 그대로 옮겨 적습니다.
 *     (repo-id, category, category-id 값)
 *  4. 이 저장소를 GitHub에 올리고 GitHub Pages를 켜면 댓글창이 표시됩니다.
 *     (설정 전까지는 댓글창 자리에 안내 문구만 보입니다.)
 */
window.GISCUS_CONFIG = {
  repo: "hyryu64/project-zero-archive",      // 예: "gh-corp/project-zero-archive"
  repoId: "R_kgDOUM3dbQ",                       // giscus.app 에서 발급되는 R_xxxxxxxx 값
  category: "General",             // Discussions 카테고리 이름
  categoryId: "DIC_kwDOUM3dbc4DEx5u",                   // giscus.app 에서 발급되는 DIC_xxxxxxxx 값
  mapping: "pathname",
  reactionsEnabled: "1",            // 상단 👍 반응 = 추천 버튼 역할
  emitMetadata: "0",
  inputPosition: "top",
  theme: "light",
  lang: "ko"
};
