/* ============================================
   ReviewPilot — Frontend JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ---- Tab Switching ----
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = document.getElementById('panel-' + target);
      if (panel) panel.classList.add('active');
    });
  });

  // ---- Loading Animation ----
  const overlay = document.getElementById('loadingOverlay');
  const loadingSteps = ['step-fetch', 'step-analyze', 'step-detect', 'step-report'];
  let currentStep = 0;
  let stepInterval = null;

  function showLoading() {
    if (!overlay) return;
    overlay.classList.add('active');
    currentStep = 0;
    loadingSteps.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove('active', 'done');
        el.querySelector('.step-icon').textContent = '⏳';
      }
    });
    advanceStep();
    stepInterval = setInterval(advanceStep, 3000);
  }

  function advanceStep() {
    if (currentStep > 0 && currentStep <= loadingSteps.length) {
      const prev = document.getElementById(loadingSteps[currentStep - 1]);
      if (prev) {
        prev.classList.remove('active');
        prev.classList.add('done');
        prev.querySelector('.step-icon').textContent = '✅';
      }
    }
    if (currentStep < loadingSteps.length) {
      const curr = document.getElementById(loadingSteps[currentStep]);
      if (curr) {
        curr.classList.add('active');
        curr.querySelector('.step-icon').textContent = '🔄';
      }
    }
    currentStep++;
  }

  function hideLoading() {
    if (overlay) overlay.classList.remove('active');
    if (stepInterval) clearInterval(stepInterval);
  }

  // ---- Form Submission: PR ----
  const prForm = document.getElementById('pr-form');
  if (prForm) {
    prForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const url = document.getElementById('pr-url').value.trim();
      const token = document.getElementById('gh-token').value.trim();

      if (!url) return;

      showLoading();

      try {
        const response = await fetch('/api/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'pr',
            url: url,
            token: token || undefined
          })
        });

        const data = await response.json();

        if (!response.ok) {
          hideLoading();
          alert(data.error || 'An error occurred. Please try again.');
          return;
        }

        // Store review data and navigate to results page
        sessionStorage.setItem('reviewPilotData', JSON.stringify(data));
        window.location.href = '/review';
      } catch (err) {
        hideLoading();
        alert('Network error: ' + err.message);
      }
    });
  }

  // ---- Form Submission: Snippet ----
  const snippetForm = document.getElementById('snippet-form');
  if (snippetForm) {
    snippetForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const code = document.getElementById('code-input').value.trim();
      const language = document.getElementById('language').value;

      if (!code) return;

      showLoading();

      try {
        const response = await fetch('/api/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'snippet',
            code: code,
            language: language || undefined
          })
        });

        const data = await response.json();

        if (!response.ok) {
          hideLoading();
          alert(data.error || 'An error occurred. Please try again.');
          return;
        }

        sessionStorage.setItem('reviewPilotData', JSON.stringify(data));
        window.location.href = '/review';
      } catch (err) {
        hideLoading();
        alert('Network error: ' + err.message);
      }
    });
  }

  // ---- Smooth scroll for anchor links ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ---- Issue Filters (review page) ----
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const filter = this.dataset.filter;
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      document.querySelectorAll('.issue-card').forEach(card => {
        if (filter === 'all' || card.dataset.severity === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

});


// ============================================
// Review Page Rendering Functions
// ============================================

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function renderReview(data) {
  // Set timestamp
  const timestamp = document.getElementById('review-timestamp');
  if (timestamp) {
    timestamp.textContent = '📅 ' + new Date().toLocaleString();
  }

  // PR Info
  if (data.pr_info) {
    const prBar = document.getElementById('pr-info-bar');
    if (prBar) {
      prBar.style.display = '';
      document.getElementById('pr-title').textContent = data.pr_info.title || 'Pull Request';
      document.getElementById('pr-author').innerHTML = '👤 ' + escapeHtml(data.pr_info.author);
      document.getElementById('pr-additions').textContent = '+' + (data.pr_info.additions || 0);
      document.getElementById('pr-deletions').textContent = '-' + (data.pr_info.deletions || 0);
      document.getElementById('pr-files').textContent = '📁 ' + (data.pr_info.changed_files || 0) + ' files';
    }
  }

  // Risk Gauge
  renderRiskGauge(data.riskScore || 0, data.overallRisk || 'low');

  // Summary
  const summaryEl = document.getElementById('risk-summary-text');
  if (summaryEl) summaryEl.textContent = data.summary || 'Analysis complete.';

  // Stats
  const stats = data.statistics || {};
  setStatValue('stat-bugs', stats.bugs || 0);
  setStatValue('stat-security', stats.security || 0);
  setStatValue('stat-performance', stats.performance || 0);
  setStatValue('stat-style', stats.style || 0);
  setStatValue('stat-total', stats.total || 0);

  // Positives
  if (data.positives && data.positives.length > 0) {
    const posSection = document.getElementById('positives-section');
    const posList = document.getElementById('positives-list');
    if (posSection && posList) {
      posSection.style.display = '';
      posList.innerHTML = data.positives
        .map(p => '<li>' + escapeHtml(p) + '</li>')
        .join('');
    }
  }

  // Issues
  renderIssues(data.issues || []);

  // Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    const recSection = document.getElementById('recommendations-section');
    const recList = document.getElementById('recommendations-list');
    if (recSection && recList) {
      recSection.style.display = '';
      recList.innerHTML = data.recommendations
        .map(r => '<li>' + escapeHtml(r) + '</li>')
        .join('');
    }
  }

  // Hide error display
  const errorDisplay = document.getElementById('error-display');
  if (errorDisplay) errorDisplay.style.display = 'none';
}

function renderRiskGauge(score, level) {
  const circle = document.getElementById('risk-gauge-circle');
  const scoreEl = document.getElementById('risk-score-value');
  const labelEl = document.getElementById('risk-level-label');

  if (!circle || !scoreEl || !labelEl) return;

  const circumference = 326.73; // 2 * π * 52
  const offset = circumference - (score / 100) * circumference;

  // Color based on risk level
  const colors = {
    low: '#10b981',
    medium: '#eab308',
    high: '#f97316',
    critical: '#ef4444'
  };

  const color = colors[level] || colors.medium;
  circle.style.stroke = color;
  scoreEl.style.color = color;
  labelEl.style.color = color;

  // Animate
  setTimeout(() => {
    circle.style.strokeDashoffset = offset;
  }, 300);

  scoreEl.textContent = score;
  labelEl.textContent = (level || 'unknown').toUpperCase();
}

function setStatValue(id, value) {
  const el = document.getElementById(id);
  if (el) {
    // Animate counting
    let current = 0;
    const target = parseInt(value) || 0;
    if (target === 0) {
      el.textContent = '0';
      return;
    }
    const step = Math.max(1, Math.floor(target / 20));
    const interval = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(interval);
      }
      el.textContent = current;
    }, 50);
  }
}

function renderIssues(issues) {
  const container = document.getElementById('issues-list');
  if (!container) return;

  if (issues.length === 0) {
    container.innerHTML = `
      <div class="no-issues">
        <div class="big-icon">🎉</div>
        <h3>No Issues Found</h3>
        <p>Your code looks great! No significant issues were detected.</p>
      </div>
    `;
    return;
  }

  // Sort: critical first, then high, medium, low, info
  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  issues.sort((a, b) => (order[a.severity] || 4) - (order[b.severity] || 4));

  container.innerHTML = issues.map((issue, i) => `
    <div class="issue-card" data-severity="${escapeHtml(issue.severity)}" data-category="${escapeHtml(issue.category)}" id="issue-${i}">
      <div class="issue-header" onclick="toggleIssue(${i})">
        <span class="severity-badge ${escapeHtml(issue.severity)}">${escapeHtml(issue.severity)}</span>
        <span class="category-badge">${getCategoryIcon(issue.category)} ${escapeHtml(issue.category)}</span>
        <div class="issue-title-area">
          <div class="issue-title">${escapeHtml(issue.title)}</div>
          <div class="issue-desc-preview">${escapeHtml(issue.description ? issue.description.substring(0, 100) : '')}</div>
        </div>
        <span class="issue-toggle">▼</span>
      </div>
      <div class="issue-body">
        <div class="issue-description">${escapeHtml(issue.description)}</div>
        ${issue.codeSnippet ? `
          <div class="code-block">
            <div class="code-block-header">Problematic Code</div>
            <pre><code>${escapeHtml(issue.codeSnippet)}</code></pre>
          </div>
        ` : ''}
        ${issue.suggestion ? `
          <div class="suggestion-block">
            <h4>💡 Suggested Fix</h4>
            <code>${escapeHtml(issue.suggestion)}</code>
          </div>
        ` : ''}
        ${issue.explanation ? `
          <div class="explanation-block">
            <h4>📘 Why This Matters</h4>
            <p>${escapeHtml(issue.explanation)}</p>
          </div>
        ` : ''}
      </div>
    </div>
  `).join('');
}

function getCategoryIcon(category) {
  const icons = {
    bug: '🐛',
    security: '🔒',
    performance: '⚡',
    style: '🎨',
    maintainability: '🔧'
  };
  return icons[category] || '📌';
}

function toggleIssue(index) {
  const card = document.getElementById('issue-' + index);
  if (card) {
    card.classList.toggle('expanded');
  }
}

function showError(message) {
  // Hide main content sections
  const sections = [
    'risk-summary', 'stats-bar', 'positives-section',
    'issues-section', 'recommendations-section', 'pr-info-bar',
    'new-review-area'
  ];
  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });

  // Show error
  const errorDisplay = document.getElementById('error-display');
  const errorMessage = document.getElementById('error-message');
  if (errorDisplay && errorMessage) {
    errorDisplay.style.display = '';
    errorMessage.textContent = message;
  }
}
