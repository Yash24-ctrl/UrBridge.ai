// Set default theme to navy blue
const htmlElement = document.documentElement;
htmlElement.setAttribute('data-theme', 'blue');
document.body.setAttribute('data-theme', 'blue');

// Loading animation helper
let loadingStartTime = 0;
let progressInterval = null;
let navigationController = null;
let pageNavigationInitialized = false;
let loadingDelayTimer = null;
let loadingVisible = false;
const MIN_LOADING_TIME = 180;
const LOADER_SHOW_DELAY = 120;

// Progress steps for resume analysis
const progressSteps = [
  'Analyzing resume structure...',
  'Extracting key information...',
  'Evaluating experience and skills...',
  'Assessing qualifications...',
  'Generating detailed insights...',
  'Finalizing comprehensive report...'
];

function getLoadingOverlay() {
  return document.getElementById('loadingOverlay');
}

function clearLoadingDelay() {
  if (loadingDelayTimer) {
    clearTimeout(loadingDelayTimer);
    loadingDelayTimer = null;
  }
}

function showLoading(message = 'Processing your resume', options = {}) {
  clearLoadingDelay();

  const { immediate = true } = options;
  if (!immediate) {
    loadingDelayTimer = setTimeout(() => {
      showLoading(message, { immediate: true });
    }, LOADER_SHOW_DELAY);
    return;
  }

  const loadingOverlay = getLoadingOverlay();
  if (loadingOverlay) {
    const loaderText = loadingOverlay.querySelector('.loader-text');
    const progressStepsEl = loadingOverlay.querySelector('.progress-steps');
    const particlesContainer = loadingOverlay.querySelector('#loadingParticles');
    const isCompactView = window.matchMedia('(max-width: 1023px)').matches;
    
    if (loaderText) loaderText.innerHTML = message + '<span class="progress-dots"></span>';
    if (progressStepsEl) progressStepsEl.textContent = 'Opening page...';
    
    loadingOverlay.classList.add('active');
    loadingStartTime = Date.now();
    loadingVisible = true;
    
    // Generate floating particles
    if (particlesContainer) {
      particlesContainer.innerHTML = '';
      const particleCount = isCompactView ? 0 : 8;
      
      for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('loading-particle');
        
        // Random size between 2px and 8px
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Random position
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        // Random animation delay and duration
        const delay = Math.random() * 2;
        const duration = 3 + Math.random() * 2;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;
        
        // Random hue rotation for variety
        const hue = Math.random() * 360;
        particle.style.filter = `hue-rotate(${hue}deg)`;
        
        particlesContainer.appendChild(particle);
      }
    }
    
    // Cycle through progress steps
    let stepIndex = 0;
    progressInterval = setInterval(() => {
      if (progressStepsEl) {
        progressStepsEl.textContent = progressSteps[stepIndex];
        if (!isCompactView) {
          progressStepsEl.style.animation = 'textGlow 0.45s ease-in-out';
        }
        
        // Remove animation class after it completes
        setTimeout(() => {
          if (progressStepsEl) {
            progressStepsEl.style.animation = '';
          }
        }, 450);
      }
      stepIndex = (stepIndex + 1) % progressSteps.length;
    }, 550);
  }
}

function hideLoading() {
  clearLoadingDelay();

  const loadingOverlay = getLoadingOverlay();
  if (loadingOverlay) {
    // Clear progress interval
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    
    if (!loadingVisible) {
      loadingOverlay.classList.remove('active');
      return;
    }

    const elapsedTime = Date.now() - loadingStartTime;
    const remainingTime = Math.max(0, MIN_LOADING_TIME - elapsedTime);

    setTimeout(() => {
      loadingOverlay.classList.remove('active');
      loadingVisible = false;
    }, remainingTime);
  }
}

function initializeFormLoading() {
  if (document.body.dataset.formLoadingBound === 'true') {
    return;
  }

  document.body.dataset.formLoadingBound = 'true';
  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }

    if (
      form.querySelector('textarea') ||
      form.querySelector('input[type="file"]') ||
      form.querySelector('input[name="username"]') ||
      form.querySelector('input[name="password"]')
    ) {
      showLoading();
    }
  });
}

function initializeDynamicFields(root = document) {
  // Handle notice period dropdown for index.html
  const noticePeriodSelect = root.getElementById ? root.getElementById('notice_period_days_IT') : root.querySelector('#notice_period_days_IT');
  const customNoticeInput = root.getElementById ? root.getElementById('custom_notice_period') : root.querySelector('#custom_notice_period');
  
  if (noticePeriodSelect && customNoticeInput && !noticePeriodSelect.dataset.bound) {
    noticePeriodSelect.dataset.bound = 'true';
    noticePeriodSelect.addEventListener('change', function() {
      if (this.value === 'custom') {
        customNoticeInput.style.display = 'block';
      } else {
        customNoticeInput.style.display = 'none';
      }
    });
  }
  
  // Handle notice period dropdown for jobmatch.html
  const noticePeriodSelectJm = root.getElementById ? root.getElementById('notice_period_days_IT_jm') : root.querySelector('#notice_period_days_IT_jm');
  const customNoticeInputJm = root.getElementById ? root.getElementById('custom_notice_period_jm') : root.querySelector('#custom_notice_period_jm');
  
  if (noticePeriodSelectJm && customNoticeInputJm && !noticePeriodSelectJm.dataset.bound) {
    noticePeriodSelectJm.dataset.bound = 'true';
    noticePeriodSelectJm.addEventListener('change', function() {
      if (this.value === 'custom') {
        customNoticeInputJm.style.display = 'block';
      } else {
        customNoticeInputJm.style.display = 'none';
      }
    });
  }
  
  // Handle education level dropdown for index.html
  const educationLevelSelect = root.getElementById ? root.getElementById('education_level') : root.querySelector('#education_level');
  const customEducationInput = root.getElementById ? root.getElementById('custom_education_level') : root.querySelector('#custom_education_level');
  
  if (educationLevelSelect && customEducationInput && !educationLevelSelect.dataset.bound) {
    educationLevelSelect.dataset.bound = 'true';
    educationLevelSelect.addEventListener('change', function() {
      if (this.value === 'custom') {
        customEducationInput.style.display = 'block';
      } else {
        customEducationInput.style.display = 'none';
      }
    });
  }
  
  // Handle education level dropdown for jobmatch.html
  const educationLevelSelectJm = root.getElementById ? root.getElementById('education_level_jm') : root.querySelector('#education_level_jm');
  const customEducationInputJm = root.getElementById ? root.getElementById('custom_education_level_jm') : root.querySelector('#custom_education_level_jm');
  
  if (educationLevelSelectJm && customEducationInputJm && !educationLevelSelectJm.dataset.bound) {
    educationLevelSelectJm.dataset.bound = 'true';
    educationLevelSelectJm.addEventListener('change', function() {
      if (this.value === 'custom') {
        customEducationInputJm.style.display = 'block';
      } else {
        customEducationInputJm.style.display = 'none';
      }
    });
  }
  
  // Handle education level dropdown for manual_input.html
  const educationLevelSelectMi = root.getElementById ? root.getElementById('education_level') : root.querySelector('#education_level');
  const customEducationInputMi = root.getElementById ? root.getElementById('custom_education_level') : root.querySelector('#custom_education_level');
  
  if (educationLevelSelectMi && customEducationInputMi && !educationLevelSelectMi.dataset.manualInputBound) {
    educationLevelSelectMi.dataset.manualInputBound = 'true';
    educationLevelSelectMi.addEventListener('change', function() {
      if (this.value === 'custom') {
        customEducationInputMi.style.display = 'block';
      } else {
        customEducationInputMi.style.display = 'none';
      }
    });
  }
}

// Auto-hide on page load complete
window.addEventListener('load', function () {
  setTimeout(hideLoading, 80);
});

// Initialize push notifications
function initializePushNotifications() {
  // Check if service worker is supported
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(registration => {
      // Check if push notifications are supported
      if ('PushManager' in window) {
        // Request permission for push notifications
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            console.log('Push notifications permission granted');
            
            // Subscribe to push notifications
            registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: urlBase64ToUint8Array('YOUR_PUBLIC_VAPID_KEY_HERE')
            }).then(subscription => {
              console.log('User is subscribed to push notifications');
              
              // In a real implementation, you would send the subscription to your server
              // For now, we'll just log it
              console.log('Subscription:', subscription);
            }).catch(err => {
              console.log('Failed to subscribe user to push notifications:', err);
            });
          } else {
            console.log('Push notifications permission denied');
          }
        });
      }
    }).catch(err => {
      console.log('Service worker registration failed:', err);
    });
  }
}

// Helper function to convert base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Initialize push notifications when the page loads
// Note: In a real implementation, you would only do this after user consent
// initializePushNotifications();

function initializeResponsiveSidebar() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (!sidebar || !mainContent || !sidebarToggle || !sidebarOverlay) {
    return;
  }

  function isMobile() {
    return window.innerWidth < 1024;
  }

  function updateSidebarVisibility() {
    if (isMobile()) {
      sidebar.classList.remove('open');
      mainContent.classList.remove('shifted');
      mainContent.style.marginLeft = '0';
      sidebarToggle.style.display = 'flex';
    } else {
      sidebar.classList.add('open');
      mainContent.classList.add('shifted');
      mainContent.style.marginLeft = '';
      sidebarToggle.style.display = 'none';
      sidebarOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  if (!sidebarToggle.dataset.bound) {
    sidebarToggle.dataset.bound = 'true';
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
      if (sidebar.classList.contains('open')) {
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
      } else {
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  if (!sidebarOverlay.dataset.bound) {
    sidebarOverlay.dataset.bound = 'true';
    sidebarOverlay.addEventListener('click', function() {
      sidebar.classList.remove('open');
      sidebarOverlay.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  if (!window.__responsiveSidebarResizeBound) {
    window.__responsiveSidebarResizeBound = true;
    window.addEventListener('resize', updateSidebarVisibility);
  }

  updateSidebarVisibility();
}

function runInlineOrExternalScript(script) {
  return new Promise((resolve, reject) => {
    const newScript = document.createElement('script');

    Array.from(script.attributes).forEach((attribute) => {
      newScript.setAttribute(attribute.name, attribute.value);
    });

    newScript.dataset.pageScript = 'true';

    if (script.src) {
      const existingScript = document.querySelector(`script[src="${script.src}"]`);
      if (existingScript) {
        resolve();
        return;
      }

      newScript.addEventListener('load', resolve, { once: true });
      newScript.addEventListener('error', reject, { once: true });
      document.body.appendChild(newScript);
      return;
    }

    newScript.textContent = script.textContent;
    document.body.appendChild(newScript);
    resolve();
  });
}

function syncPageAssets(nextDocument) {
  document.head.querySelectorAll('[data-page-asset="true"]').forEach((asset) => asset.remove());

  nextDocument.head.querySelectorAll('link[rel="stylesheet"], style').forEach((asset) => {
    if (asset.dataset.staticAsset === 'true') {
      return;
    }

    const clonedAsset = asset.cloneNode(true);
    clonedAsset.dataset.pageAsset = 'true';
    document.head.appendChild(clonedAsset);
  });
}

async function runPageScripts(nextDocument) {
  document.querySelectorAll('script[data-page-script="true"]').forEach((script) => script.remove());

  const scripts = Array.from(nextDocument.body.querySelectorAll('script')).filter(
    (script) => script.dataset.staticScript !== 'true'
  );

  for (const script of scripts) {
    await runInlineOrExternalScript(script);
  }

  document.dispatchEvent(new Event('DOMContentLoaded'));
}

function shouldBypassPartialNavigation(url, link) {
  if (link.hasAttribute('download') || link.dataset.fullReload === 'true') {
    return true;
  }

  if (link.target && link.target !== '_self') {
    return true;
  }

  if (url.origin !== window.location.origin) {
    return true;
  }

  if (url.pathname.startsWith('/static/')) {
    return true;
  }

  const bypassPaths = ['/logout', '/export', '/performance/export', '/api/roadmap/export'];
  return bypassPaths.some((path) => url.pathname.startsWith(path));
}

async function navigateTo(url, options = {}) {
  const targetUrl = typeof url === 'string' ? new URL(url, window.location.origin) : url;

  if (navigationController) {
    navigationController.abort();
  }

  navigationController = new AbortController();
  showLoading('Loading page', { immediate: false });

  try {
    const response = await fetch(targetUrl.toString(), {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      signal: navigationController.signal
    });

    if (response.redirected) {
      window.location.href = response.url;
      return;
    }

    const contentType = response.headers.get('content-type') || '';
    if (!response.ok || !contentType.includes('text/html')) {
      window.location.href = targetUrl.toString();
      return;
    }

    const html = await response.text();
    const parser = new DOMParser();
    const nextDocument = parser.parseFromString(html, 'text/html');
    const nextMainContent = nextDocument.getElementById('mainContent');
    const currentMainContent = document.getElementById('mainContent');

    if (!nextMainContent || !currentMainContent) {
      window.location.href = targetUrl.toString();
      return;
    }

    syncPageAssets(nextDocument);
    currentMainContent.innerHTML = nextMainContent.innerHTML;
    document.title = nextDocument.title || document.title;

    if (!options.replaceState) {
      window.history.pushState({ path: targetUrl.toString() }, '', targetUrl.toString());
    }

    window.scrollTo({ top: 0, behavior: 'auto' });
    initializePageUI(document);
    await runPageScripts(nextDocument);
  } catch (error) {
    if (error.name !== 'AbortError') {
      window.location.href = targetUrl.toString();
    }
  } finally {
    hideLoading();
  }
}

function initializePartialNavigation() {
  if (pageNavigationInitialized) {
    return;
  }

  pageNavigationInitialized = true;

  document.addEventListener('click', function(event) {
    const link = event.target.closest('a[href]');
    if (!link) {
      return;
    }

    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }

    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) {
      return;
    }

    const targetUrl = new URL(href, window.location.origin);
    if (shouldBypassPartialNavigation(targetUrl, link)) {
      return;
    }

    event.preventDefault();
    navigateTo(targetUrl);
  });

  window.addEventListener('popstate', function() {
    navigateTo(window.location.href, { replaceState: true });
  });
}

function initializePageUI(root = document) {
  initializeFormLoading();
  initializeDynamicFields(root);
  initializeResponsiveSidebar();
}

document.addEventListener('DOMContentLoaded', function() {
  initializePageUI(document);
  initializePartialNavigation();
});


