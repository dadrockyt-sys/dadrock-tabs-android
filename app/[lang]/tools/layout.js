import { generateAlternates, generateCanonical } from '@/lib/seo';

const toolsMeta = {
  en: {
    title: 'Free Guitar Practice Tools | DadRock Tabs',
    description: 'Use free guitar practice tools from DadRock Tabs, including a metronome, reference tuner, and chord reference for guitar and bass players.',
  },
  es: {
    title: 'Herramientas Gratis para Practicar Guitarra | DadRock Tabs',
    description: 'Practica guitarra y bajo gratis con metrónomo, afinador de referencia y guía de acordes de DadRock Tabs.',
  },
  pt: {
    title: 'Ferramentas Grátis para Praticar Guitarra | DadRock Tabs',
    description: 'Pratique guitarra e baixo gratuitamente com metrónomo, afinador de referência e guia de acordes do DadRock Tabs.',
  },
  'pt-br': {
    title: 'Ferramentas Grátis para Praticar Guitarra | DadRock Tabs',
    description: 'Pratique guitarra, violão e baixo grátis com metrônomo, afinador de referência e guia de acordes do DadRock Tabs.',
  },
  de: {
    title: 'Kostenlose Gitarren-Übungstools | DadRock Tabs',
    description: 'Übe Gitarre und Bass kostenlos mit Metronom, Referenz-Stimmgerät und Akkordübersicht von DadRock Tabs.',
  },
  fr: {
    title: 'Outils Gratuits pour Pratiquer la Guitare | DadRock Tabs',
    description: 'Travaillez la guitare et la basse gratuitement avec un métronome, un accordeur de référence et un guide d’accords.',
  },
  it: {
    title: 'Strumenti Gratuiti per Esercitarsi con la Chitarra | DadRock Tabs',
    description: 'Esercitati con chitarra e basso usando gratuitamente metronomo, accordatore di riferimento e guida agli accordi.',
  },
  ja: {
    title: '無料ギター練習ツール | DadRock Tabs',
    description: 'メトロノーム、基準チューナー、コードリファレンスを無料で使ってギターとベースを練習できます。',
  },
  ko: {
    title: '무료 기타 연습 도구 | DadRock Tabs',
    description: '메트로놈, 기준 튜너, 코드 참고표를 무료로 사용해 기타와 베이스를 연습하세요.',
  },
  zh: {
    title: '免费吉他练习工具 | DadRock Tabs',
    description: '免费使用节拍器、参考调音器和和弦参考工具练习吉他和贝斯。',
  },
  ru: {
    title: 'Бесплатные инструменты для занятий на гитаре | DadRock Tabs',
    description: 'Занимайтесь на гитаре и басу бесплатно с метрономом, эталонным тюнером и справочником аккордов.',
  },
  hi: {
    title: 'मुफ्त गिटार अभ्यास उपकरण | DadRock Tabs',
    description: 'मेट्रोनोम, रेफरेंस ट्यूनर और कॉर्ड रेफरेंस के साथ गिटार और बास का मुफ्त अभ्यास करें।',
  },
  sv: {
    title: 'Gratis övningsverktyg för gitarr | DadRock Tabs',
    description: 'Öva gitarr och bas gratis med metronom, referensstämmare och ackordreferens från DadRock Tabs.',
  },
  fi: {
    title: 'Ilmaiset kitaran harjoittelutyökalut | DadRock Tabs',
    description: 'Harjoittele kitaraa ja bassoa ilmaiseksi metronomin, vertailuvirittimen ja sointuoppaan avulla.',
  },
};

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/tools', lang);
  const meta = toolsMeta[lang] || toolsMeta.en;

  return {
    title: meta.title,
    description: meta.description,
    alternates: generateAlternates('/tools', lang),
    openGraph: {
      title: meta.title,
      description: meta.description,
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title: meta.title,
      description: meta.description,
    },
  };
}

export default function LocalizedToolsLayout({ children }) {
  return children;
}
