import { generateAlternates, generateCanonical } from '@/lib/seo';

const whatsNewMeta = {
  en: {
    title: "What's New - Latest Guitar & Bass Lessons | DadRock Tabs",
    description: 'See the latest guitar and bass tab lessons, tutorials, and newly added songs on DadRock Tabs.',
  },
  es: {
    title: 'Novedades - Últimas Lecciones de Guitarra y Bajo | DadRock Tabs',
    description: 'Descubre las últimas lecciones de guitarra y bajo, tutoriales y canciones nuevas añadidas a DadRock Tabs.',
  },
  pt: {
    title: 'Novidades - Últimas Aulas de Guitarra e Baixo | DadRock Tabs',
    description: 'Veja as últimas aulas de guitarra e baixo, tutoriais e músicas adicionadas recentemente ao DadRock Tabs.',
  },
  'pt-br': {
    title: 'Novidades - Últimas Aulas de Guitarra e Baixo | DadRock Tabs',
    description: 'Veja as últimas aulas de guitarra e baixo, tutoriais e músicas adicionadas recentemente ao DadRock Tabs.',
  },
  de: {
    title: 'Neuigkeiten - Neue Gitarren- & Bass-Lektionen | DadRock Tabs',
    description: 'Entdecke die neuesten Gitarren- und Bass-Tab-Lektionen, Tutorials und neu hinzugefügten Songs bei DadRock Tabs.',
  },
  fr: {
    title: 'Nouveautés - Dernières Leçons de Guitare et Basse | DadRock Tabs',
    description: 'Découvrez les dernières leçons de guitare et basse, les tutoriels et les chansons récemment ajoutées sur DadRock Tabs.',
  },
  it: {
    title: 'Novità - Ultime Lezioni di Chitarra e Basso | DadRock Tabs',
    description: 'Scopri le ultime lezioni di chitarra e basso, i tutorial e i brani appena aggiunti su DadRock Tabs.',
  },
  ja: {
    title: '最新情報 - 新着ギター＆ベースレッスン | DadRock Tabs',
    description: 'DadRock Tabsに追加された最新のギター＆ベースタブレッスン、チュートリアル、楽曲をチェック。',
  },
  ko: {
    title: '새로운 소식 - 최신 기타 & 베이스 레슨 | DadRock Tabs',
    description: 'DadRock Tabs에 새로 추가된 기타 및 베이스 탭 레슨, 튜토리얼과 곡을 확인하세요.',
  },
  zh: {
    title: '最新动态 - 最新吉他和贝斯课程 | DadRock Tabs',
    description: '查看DadRock Tabs最新添加的吉他和贝斯谱课程、教程及歌曲。',
  },
  ru: {
    title: 'Что нового - Новые уроки гитары и баса | DadRock Tabs',
    description: 'Смотрите новые уроки гитары и баса, табулатуры, обучающие материалы и недавно добавленные песни на DadRock Tabs.',
  },
  hi: {
    title: 'नया क्या है - नवीनतम गिटार और बास लेसन | DadRock Tabs',
    description: 'DadRock Tabs पर नवीनतम गिटार और बास टैब लेसन, ट्यूटोरियल और हाल ही में जोड़े गए गाने देखें।',
  },
  sv: {
    title: 'Nyheter - Senaste gitarr- och baslektionerna | DadRock Tabs',
    description: 'Se de senaste gitarr- och bastablektionerna, guiderna och nyligen tillagda låtarna på DadRock Tabs.',
  },
  fi: {
    title: 'Uutta - Uusimmat kitara- ja bassotunnit | DadRock Tabs',
    description: 'Katso DadRock Tabsien uusimmat kitara- ja bassotabulatuurit, oppaat ja äskettäin lisätyt kappaleet.',
  },
};

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/whats-new', lang);
  const meta = whatsNewMeta[lang] || whatsNewMeta.en;

  return {
    title: meta.title,
    description: meta.description,
    alternates: generateAlternates('/whats-new', lang),
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

export default function LocalizedWhatsNewLayout({ children }) {
  return children;
}
