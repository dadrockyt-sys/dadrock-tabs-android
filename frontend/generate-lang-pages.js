const fs = require('fs');
const path = require('path');

// Language configurations
const languages = {
  'en': {
    lang: 'en',
    title: 'DadRock Tabs - Free Guitar & Bass Tabs | Classic Rock, Hair Metal, Blues',
    description: 'Free guitar and bass tabs with video lessons for classic rock, 80s hair metal, and blues. Search 4000+ tutorials. Learn Led Zeppelin, AC/DC, Van Halen and more!',
    canonical: 'https://dadrocktabs.com/'
  },
  'es': {
    lang: 'es',
    title: 'DadRock Tabs - Tablaturas Gratis de Guitarra y Bajo | Rock Clásico',
    description: 'Tablaturas gratis de guitarra y bajo con lecciones en video para rock clásico, hair metal de los 80s y blues. Busca más de 4000 tutoriales.',
    canonical: 'https://dadrocktabs.com/es/'
  },
  'pt-br': {
    lang: 'pt-BR',
    title: 'DadRock Tabs - Tablaturas Grátis de Guitarra e Baixo | Rock Clássico',
    description: 'Tablaturas grátis de guitarra e baixo com vídeo aulas para rock clássico, hair metal dos anos 80 e blues. Pesquise mais de 4000 tutoriais.',
    canonical: 'https://dadrocktabs.com/pt-br/'
  },
  'fr': {
    lang: 'fr',
    title: 'DadRock Tabs - Tablatures Gratuites Guitare & Basse | Rock Classique',
    description: 'Tablatures gratuites de guitare et basse avec leçons vidéo pour rock classique, hair metal des années 80 et blues. Recherchez plus de 4000 tutoriels.',
    canonical: 'https://dadrocktabs.com/fr/'
  },
  'de': {
    lang: 'de',
    title: 'DadRock Tabs - Kostenlose Gitarren- & Bass-Tabs | Classic Rock',
    description: 'Kostenlose Gitarren- und Bass-Tabs mit Video-Lektionen für Classic Rock, 80er Hair Metal und Blues. Über 4000 Tutorials durchsuchen.',
    canonical: 'https://dadrocktabs.com/de/'
  },
  'it': {
    lang: 'it',
    title: 'DadRock Tabs - Tablature Gratuite Chitarra e Basso | Rock Classico',
    description: 'Tablature gratuite per chitarra e basso con video lezioni per rock classico, hair metal anni 80 e blues. Cerca oltre 4000 tutorial.',
    canonical: 'https://dadrocktabs.com/it/'
  },
  'ja': {
    lang: 'ja',
    title: 'DadRock Tabs - 無料ギター＆ベースタブ譜 | クラシックロック',
    description: 'クラシックロック、80年代ヘアメタル、ブルースのビデオレッスン付き無料ギター・ベースタブ譜。4000以上のチュートリアルを検索。',
    canonical: 'https://dadrocktabs.com/ja/'
  },
  'ru': {
    lang: 'ru',
    title: 'DadRock Tabs - Бесплатные Табы для Гитары и Баса | Классический Рок',
    description: 'Бесплатные табы для гитары и баса с видео уроками для классического рока, хэйр-метала 80-х и блюза. Ищите среди 4000+ туториалов.',
    canonical: 'https://dadrocktabs.com/ru/'
  },
  'hi': {
    lang: 'hi',
    title: 'DadRock Tabs - मुफ़्त गिटार और बेस टैब्स | क्लासिक रॉक',
    description: 'क्लासिक रॉक, 80 के दशक के हेयर मेटल और ब्लूज़ के लिए वीडियो पाठों के साथ मुफ़्त गिटार और बेस टैब्स। 4000+ ट्यूटोरियल खोजें।',
    canonical: 'https://dadrocktabs.com/hi/'
  }
};

const buildDir = path.join(__dirname, 'build');
const indexPath = path.join(buildDir, 'index.html');

console.log('🌍 Generating language-specific HTML files...\n');

// Read the original index.html
let originalHtml = fs.readFileSync(indexPath, 'utf8');

// Process each language
Object.entries(languages).forEach(([langCode, config]) => {
  console.log(`📝 Processing ${langCode.toUpperCase()} (${config.lang})...`);
  
  let html = originalHtml;
  
  // 1. Set the correct lang attribute on <html>
  html = html.replace(/<html lang="[^"]*"/, `<html lang="${config.lang}"`);
  
  // 2. Replace ALL occurrences of dynamic canonical with static one
  // Handle minified version where it appears as string concatenation
  // The minified code might look like: "https://dadrocktabs.com"+(e||"")+"/"
  // We need to replace window.__DADROCK_CANONICAL assignments and usages
  
  // Replace the assignment in the first script
  html = html.replace(
    /window\.__DADROCK_CANONICAL="https:\/\/dadrocktabs\.com"\+\([^)]+\)\+"\/"/g,
    `window.__DADROCK_CANONICAL="${config.canonical}"`
  );
  
  // Replace document.write for canonical link
  html = html.replace(
    /document\.write\('<link rel="canonical" href="'\+window\.__DADROCK_CANONICAL\+'" \/>'\)/g,
    ''
  );
  html = html.replace(
    /document\.write\('<link rel="canonical" href="'\+"https:\/\/dadrocktabs\.com\/fr\/"\+'" \/>'\)/g,
    ''
  );
  
  // Remove any existing dynamic canonical scripts and add static canonical
  html = html.replace(
    /<script>document\.write\('<link rel="canonical"[^<]*<\/script>/g,
    ''
  );
  
  // Add static canonical link after robots meta
  if (!html.includes(`<link rel="canonical" href="${config.canonical}"`)) {
    html = html.replace(
      /<meta name="robots"[^>]*>/,
      `$&\n<link rel="canonical" href="${config.canonical}" />`
    );
  }
  
  // Replace dynamic og:url
  html = html.replace(
    /<script>document\.write\('<meta property="og:url"[^<]*<\/script>/g,
    `<meta property="og:url" content="${config.canonical}" />`
  );
  
  // Replace dynamic twitter:url  
  html = html.replace(
    /<script>document\.write\('<meta name="twitter:url"[^<]*<\/script>/g,
    `<meta name="twitter:url" content="${config.canonical}" />`
  );
  
  // 3. Add static title if not present (after </head> opening scripts)
  // First remove any dynamic title generation
  html = html.replace(/document\.write\("<title>"\+[^)]+\+"<\/title>"\)/g, '');
  html = html.replace(/document\.write\('<title>'\+[^)]+\+'<\/title>'\)/g, '');
  
  // Add title right after <head>
  if (!html.includes(`<title>${config.title}</title>`)) {
    html = html.replace(/<head>/, `<head>\n<title>${config.title}</title>`);
  }
  
  // 4. Update meta description
  html = html.replace(
    /<meta name="description" content="[^"]*"/,
    `<meta name="description" content="${config.description}"`
  );
  
  // 5. Update og:title and og:description
  html = html.replace(
    /<meta property="og:title" content="[^"]*"/,
    `<meta property="og:title" content="${config.title}"`
  );
  html = html.replace(
    /<meta property="og:description" content="[^"]*"/,
    `<meta property="og:description" content="${config.description}"`
  );
  
  // 6. Remove all seo-lang sections EXCEPT the current language
  const allLangCodes = Object.keys(languages);
  
  allLangCodes.forEach(otherLang => {
    if (otherLang !== langCode) {
      // Remove the entire div for other languages - handle both minified and non-minified
      // Pattern: <div id="seo-XX" class="seo-lang" ...>...</div>
      const patterns = [
        // Non-minified with hidden attribute
        new RegExp(`<div id="seo-${otherLang}" class="seo-lang" hidden[^>]*>[\\s\\S]*?<\\/div>\\s*(?=<div id="seo-|<!-- Shared)`, 'g'),
        // Minified version
        new RegExp(`<div id="seo-${otherLang}" class="seo-lang"[^>]*>[\\s\\S]*?<\\/div>(?=<div id="seo-|<div id="seo-shared)`, 'g'),
      ];
      
      patterns.forEach(regex => {
        html = html.replace(regex, '');
      });
    }
  });
  
  // 7. Make the current language section visible
  html = html.replace(
    new RegExp(`<div id="seo-${langCode}" class="seo-lang" hidden`, 'g'),
    `<div id="seo-${langCode}" class="seo-lang"`
  );
  html = html.replace(
    new RegExp(`id="seo-${langCode}" class="seo-lang" style="display:\\s*none;?"`, 'g'),
    `id="seo-${langCode}" class="seo-lang" style="display:block"`
  );
  
  // 8. Add static JSON-LD for this language
  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": config.title,
    "description": config.description,
    "url": config.canonical,
    "inLanguage": config.lang,
    "isPartOf": {
      "@type": "WebSite",
      "name": "DadRock Tabs",
      "url": "https://dadrocktabs.com"
    }
  };
  
  // Add JSON-LD before </head>
  const jsonLdScript = `<script type="application/ld+json">${JSON.stringify(webPageJsonLd)}</script>`;
  if (!html.includes('"@type":"WebPage"')) {
    html = html.replace('</head>', `${jsonLdScript}\n</head>`);
  }
  
  // Create directory if needed
  const langDir = langCode === 'en' ? buildDir : path.join(buildDir, langCode);
  if (langCode !== 'en' && !fs.existsSync(langDir)) {
    fs.mkdirSync(langDir, { recursive: true });
  }
  
  // Write the file
  const outputPath = langCode === 'en' 
    ? indexPath 
    : path.join(langDir, 'index.html');
  
  fs.writeFileSync(outputPath, html);
  console.log(`   ✅ Written to ${outputPath}`);
});

console.log('\n🎉 Language-specific HTML generation complete!');
console.log(`   Generated ${Object.keys(languages).length} language versions.`);

