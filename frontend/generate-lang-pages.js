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
  
  // 2. Replace the dynamic canonical with a static one
  // Remove the document.write for canonical and add static link
  html = html.replace(
    /<script>document\.write\('<link rel="canonical" href="' \+ window\.__DADROCK_CANONICAL \+ '" \/>';\)<\/script>/,
    `<link rel="canonical" href="${config.canonical}" />`
  );
  
  // 3. Set static title (remove dynamic title generation and add static)
  // Find and replace the dynamic title script
  const titleScriptRegex = /document\.write\('<title>' \+ data\.title \+ '<\/title>'\);/;
  html = html.replace(titleScriptRegex, '');
  
  // Add static title tag if not present
  if (!html.includes(`<title>${config.title}</title>`)) {
    html = html.replace('</head>', `<title>${config.title}</title>\n</head>`);
  }
  
  // 4. Update meta description
  html = html.replace(
    /<meta name="description" content="[^"]*"/,
    `<meta name="description" content="${config.description}"`
  );
  
  // 5. Update og:url
  html = html.replace(
    /<script>document\.write\('<meta property="og:url" content="' \+ window\.__DADROCK_CANONICAL \+ '" \/>';\)<\/script>/,
    `<meta property="og:url" content="${config.canonical}" />`
  );
  
  // 6. Remove all seo-lang sections EXCEPT the current language
  // This is the key part - we only keep the matching language content
  const allLangCodes = Object.keys(languages);
  
  allLangCodes.forEach(otherLang => {
    if (otherLang !== langCode) {
      // Remove the entire div for other languages
      const seoRegex = new RegExp(
        `<div id="seo-${otherLang}" class="seo-lang"[^>]*>[\\s\\S]*?<\\/div>\\s*(?=<div id="seo-|<!-- Shared content)`,
        'g'
      );
      html = html.replace(seoRegex, '');
    }
  });
  
  // 7. Make the current language section visible (remove hidden attribute and display:none)
  html = html.replace(
    new RegExp(`<div id="seo-${langCode}" class="seo-lang" hidden style="display: none;">`),
    `<div id="seo-${langCode}" class="seo-lang" style="display: block;">`
  );
  html = html.replace(
    new RegExp(`<div id="seo-${langCode}" class="seo-lang" hidden>`),
    `<div id="seo-${langCode}" class="seo-lang" style="display: block;">`
  );
  
  // 8. Update JSON-LD WebPage data to be static
  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": config.title.split(' - ')[0] + ' - ' + (config.lang === 'en' ? 'Guitar & Bass Lessons' : config.title.split(' | ')[0].split(' - ')[1]),
    "description": config.description,
    "url": config.canonical,
    "inLanguage": config.lang,
    "isPartOf": {
      "@type": "WebSite",
      "name": "DadRock Tabs",
      "url": "https://dadrocktabs.com"
    }
  };
  
  // Remove dynamic JSON-LD and add static one
  // This regex finds and removes the dynamic WebPage JSON-LD script
  const jsonLdScriptRegex = /<script>\s*\(function\(\)\s*\{\s*var jsonLdData[\s\S]*?<\\\/script>'\);\s*\}\)\(\);\s*<\/script>/;
  html = html.replace(jsonLdScriptRegex, 
    `<script type="application/ld+json">${JSON.stringify(webPageJsonLd, null, 2)}</script>`
  );
  
  // 9. Clean up unnecessary dynamic scripts for this static version
  // Keep the language detection for React app functionality but the SEO content is now static
  
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
