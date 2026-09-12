/* =========================
   1. DOM 선택
========================= */

const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const navLinks = document.querySelectorAll('.nav-link');

const themeButton = document.querySelector('.theme-toggle');

const header = document.querySelector('.header');
const scrollTopButton = document.querySelector('#scroll-top');


/* =========================
   2. 상태
========================= */

const state = {
  menuOpen: false,
  theme: localStorage.getItem('theme') || 'light',

  projects : [],
  loading: false,
  error: null,

  formErrors: {
    name: '',
    email: '',
    message: ''
  }

};


/* =========================
   3. 햄버거 메뉴
========================= */

const renderMenu = () => {
  navMenu.classList.toggle('active', state.menuOpen);

  hamburger.setAttribute(
    'aria-expanded',
    state.menuOpen
  );
};

hamburger.addEventListener('click', () => {
  state.menuOpen = !state.menuOpen;

  renderMenu();
});


/* 메뉴 클릭 후 모바일 메뉴 닫기 */

navLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault();

    const target = document.querySelector(
      link.getAttribute('href')
    );

    target.scrollIntoView({
      behavior: 'smooth'
    });

    state.menuOpen = false;
    renderMenu();
  });
});


/* =========================
   4. 다크 모드
========================= */

const renderTheme = () => {
  document.documentElement.setAttribute(
    'data-theme',
    state.theme
  );

  themeButton.textContent =
    state.theme === 'dark' ? '☀️' : '🌙';
};


themeButton.addEventListener('click', () => {

  state.theme =
    state.theme === 'light'
      ? 'dark'
      : 'light';

  localStorage.setItem(
    'theme',
    state.theme
  );

  renderTheme();
});


/* 처음 페이지가 열렸을 때 적용 */
renderTheme();


/* =========================
   5. 스크롤 이벤트
========================= */

window.addEventListener('scroll', () => {

  /* 60px 이상 스크롤 → Header 배경 */
  if (window.scrollY >= 60) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }


  /* 300px 이상 → 맨 위 버튼 표시 */
  if (window.scrollY >= 300) {
    scrollTopButton.classList.add('visible');
  } else {
    scrollTopButton.classList.remove('visible');
  }

});


/* =========================
   6. 맨 위로 이동
========================= */

scrollTopButton.addEventListener('click', () => {

  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });

});


/* =========================
   7. 스크롤 애니메이션
========================= */

const sections = document.querySelectorAll('.section');

sections.forEach((section) => {
  section.classList.add('reveal');
});


const observer = new IntersectionObserver(
  (entries) => {

    entries.forEach((entry) => {

      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }

    });

  },
  {
    threshold: 0.2
  }
);


sections.forEach((section) => {
  observer.observe(section);
});


/* =========================
   8. GitHub API
========================= */

const projectStatus = document.querySelector('#project-status');
const projectList = document.querySelector('#project-list');

/* 본인 GitHub 아이디로 변경 */
const GITHUB_USERNAME = 'hyunn9799';


/* 프로젝트 화면 그리기 */
const renderProjects = () => {

  /* 로딩 */
  if (state.loading) {
    projectStatus.textContent = '프로젝트를 불러오는 중...';
    projectList.innerHTML = '';
    return;
  }

  /* 에러 */
  if (state.error) {
    projectStatus.innerHTML = `
      ${state.error}
      <button id="retry-button">다시 시도</button>
    `;

    projectList.innerHTML = '';

    const retryButton =
      document.querySelector('#retry-button');

    retryButton.addEventListener('click', loadProjects);

    return;
  }

  /* 빈 데이터 */
  if (state.projects.length === 0) {
    projectStatus.textContent =
      '표시할 프로젝트가 없습니다.';

    projectList.innerHTML = '';

    return;
  }

  /* 성공 */
  projectStatus.textContent = '';

  const cards = state.projects.map((repo) => {

    /* 구조분해 할당 */
    const {
      name,
      description,
      html_url,
      language,
      stargazers_count
    } = repo;

    return `
      <article class="project-card">

        <h3>${name}</h3>

        <p>
          ${description || '설명이 없습니다.'}
        </p>

        <p>
          언어: ${language || '기타'}
        </p>

        <p>
          ⭐ ${stargazers_count}
        </p>

        <a
          href="${html_url}"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub 보기
        </a>

      </article>
    `;
  });

  projectList.innerHTML = cards.join('');
};


/* GitHub 데이터 가져오기 */
async function loadProjects() {

  state.loading = true;
  state.error = null;

  renderProjects();

  try {

    const response = await fetch(
      `https://api.github.com/users/${GITHUB_USERNAME}/repos`
    );

    if (!response.ok) {
      throw new Error(
        response.status === 403
          ? 'GitHub API 요청 한도를 초과했습니다.'
          : '프로젝트를 불러올 수 없습니다.'
      );
    }

    const data = await response.json();


    /*
      fork 프로젝트는 제외
      → filter 사용
    */
    state.projects = data.filter(
      (repo) => !repo.fork
    );

  } catch (error) {

    state.error = error.message;

  } finally {

    state.loading = false;

    renderProjects();
  }
}


/* 페이지 시작 시 GitHub 프로젝트 호출 */
loadProjects();


/* =========================
   9. Contact Form
========================= */

const contactForm = document.querySelector('#contact-form');

const nameInput = document.querySelector('#name');
const emailInput = document.querySelector('#email');
const messageInput = document.querySelector('#message');

const nameError = document.querySelector('#name-error');
const emailError = document.querySelector('#email-error');
const messageError = document.querySelector('#message-error');

const formSuccess = document.querySelector('#form-success');


/* 이메일 형식 검사 */
const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};


/* 입력값 검사 */
const validateForm = () => {

  state.formErrors.name =
    nameInput.value.trim()
      ? ''
      : '이름을 입력해주세요.';


  state.formErrors.email =
    !emailInput.value.trim()
      ? '이메일을 입력해주세요.'
      : !isValidEmail(emailInput.value)
        ? '올바른 이메일 형식이 아닙니다.'
        : '';


  state.formErrors.message =
    messageInput.value.trim()
      ? ''
      : '메시지를 입력해주세요.';


  renderFormErrors();


  return (
    !state.formErrors.name &&
    !state.formErrors.email &&
    !state.formErrors.message
  );
};


/* 에러 화면 업데이트 */
const renderFormErrors = () => {

  nameError.textContent =
    state.formErrors.name;

  emailError.textContent =
    state.formErrors.email;

  messageError.textContent =
    state.formErrors.message;
};


/* 제출 */
contactForm.addEventListener('submit', (event) => {

  event.preventDefault();

  formSuccess.textContent = '';

  const isValid = validateForm();

  if (!isValid) {
    return;
  }

  formSuccess.textContent =
    '메시지가 정상적으로 확인되었습니다.';

  contactForm.reset();
});

/* 입력 중 즉시 다시 검사 */
nameInput.addEventListener('input', () => {
  validateForm();
});

emailInput.addEventListener('input', () => {
  validateForm();
});

messageInput.addEventListener('input', () => {
  validateForm();
});