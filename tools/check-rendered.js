/* Run in a rendered Marp HTML page. No Node.js or browser extension required.
   Paste this file in DevTools, then: await aizomeCheck()
   Uses layout measurements; passing does not replace visual review. */
(() => {
  'use strict';
  window.aizomeCheck = async function ({ timeoutMs = 8000 } = {}) {
    const findings = [], seen = new Set(), originalHash = location.hash;
    const add = (severity, code, slide, message, element) => {
      const target = element ? `${element.tagName.toLowerCase()}: ${(element.textContent || element.getAttribute('alt') || '').trim().slice(0, 60)}` : '';
      const key = [severity, code, slide, target].join('|');
      if (!seen.has(key)) findings.push({ severity, code, slide, message, target });
      seen.add(key);
    };
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
    const wait = promise => Promise.race([promise, delay(timeoutMs)]);
    const slides = [...document.querySelectorAll('section[id]')].filter(s => /^\d+$/.test(s.id));
    if (!slides.length) add('error', 'not-a-deck', null, 'Marpのスライドが見つかりません。');
    await wait(document.fonts.ready);
    // Explicitly load the bundled faces so a missing font cannot silently pass as fallback.
    for (const weight of [400, 500, 700]) {
      try {
        const loaded = await wait(document.fonts.load(`${weight} 24px "M PLUS Rounded 1c"`, '確認'));
        if (!loaded?.length) add('error', 'font-unavailable', null, `Rounded 1c (${weight}) を読み込めません。`);
      } catch { add('error', 'font-unavailable', null, `Rounded 1c (${weight}) を読み込めません。`); }
    }
    await wait(Promise.all([...document.images].map(img => img.decode().catch(() => {}))));
    // Marp's full-slide images are CSS backgrounds, not document.images.
    const backgrounds = new Map();
    for (const e of document.querySelectorAll('section,figure,[style*="background"]')) {
      const value = getComputedStyle(e).backgroundImage;
      for (const match of value.matchAll(/url\(["']?(.*?)["']?\)/g)) {
        if (!backgrounds.has(match[1])) backgrounds.set(match[1], e);
      }
    }
    for (const [url, e] of backgrounds) {
      const img = new Image(); img.src = url;
      const ok = await wait(img.decode().then(() => true).catch(() => false));
      if (!ok) add('error', 'missing-background', e.closest('svg')?.querySelector('section[id]')?.id || null, '背景画像を読み込めません。', e);
    }
    try {
      for (const slide of slides) {
        location.hash = slide.id;
        await delay(35);
        const box = slide.getBoundingClientRect();
        const scale = box.width / 1280;
        if (!scale || !box.height) {
          add('error', 'not-visible', slide.id, 'スライドの寸法を取得できません。');
          continue;
        }
        const visible = e => {
          const r = e.getBoundingClientRect();
          return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden';
        };
        for (const e of slide.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,pre,table,img,header,footer')) {
          if (!visible(e)) continue;
          const r = e.getBoundingClientRect(), tolerance = 2 * scale;
          if (r.left < box.left - tolerance || r.right > box.right + tolerance || r.top < box.top - tolerance || r.bottom > box.bottom + tolerance)
            add('error', 'overflow', slide.id, '要素がスライドからはみ出しています。', e);
          if (e.tagName === 'PRE' && (e.scrollWidth > e.clientWidth + 2 || e.scrollHeight > e.clientHeight + 2))
            add('error', 'clipped-code', slide.id, 'コードが枠内で切れています。', e);
          if (e.tagName === 'IMG' && (!e.complete || !e.naturalWidth))
            add('error', 'missing-image', slide.id, '画像を読み込めません。外部画像は接続も確認してください。', e);
          if (e.tagName === 'IMG' && !e.classList.contains('emoji') && !e.getAttribute('alt'))
            add('warning', 'image-description', slide.id, '画像の説明を確認してください。', e);
        }
        const title = slide.querySelector(':scope > h1');
        const notes = slide.classList.contains('with-notes') ? slide.lastElementChild : slide.querySelector(':scope > footer');
        const body = [...slide.children].filter(e => !['H1', 'HEADER', 'FOOTER'].includes(e.tagName) && e !== notes && visible(e));
        if (title && visible(title) && !['cover','section','closing','full-image','profile'].some(c => slide.classList.contains(c))) {
          const bottom = title.getBoundingClientRect().bottom;
          for (const e of body) if (e.getBoundingClientRect().top < bottom + 12 * scale)
            add('error', 'title-clearance', slide.id, 'タイトルと本文の間隔が不足しています。', e);
          const header = slide.querySelector(':scope > header');
          if (header && visible(header) && header.getBoundingClientRect().bottom > title.getBoundingClientRect().top)
            add('error', 'header-overlap', slide.id, 'セクション名とタイトルが重なっています。', header);
        }
        if (notes && visible(notes) && (slide.classList.contains('with-notes') || slide.classList.contains('with-source'))) {
          for (const e of body) if (e.getBoundingClientRect().bottom > notes.getBoundingClientRect().top - 16 * scale)
            add('error', 'notes-clearance', slide.id, '本文と出典・注釈の間隔が不足しています。', e);
        }
      }
      for (const a of document.querySelectorAll('a[href^="#"]')) {
        const fragment = a.getAttribute('href').slice(1);
        let decoded = fragment;
        try { decoded = decodeURIComponent(fragment); } catch {}
        if (fragment && !document.getElementById(fragment) && !document.getElementById(decoded))
          add('error', 'broken-fragment', a.closest('section')?.id || null, 'ページ内リンク先がありません。', a);
      }
    } finally { location.hash = originalHash; }
    const result = { schemaVersion: 1, scope: 'rendered-html', slides: slides.length,
      errors: findings.filter(f => f.severity === 'error').length,
      warnings: findings.filter(f => f.severity === 'warning').length, findings };
    console.table(findings);
    return result;
  };
})();
