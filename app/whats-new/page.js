'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSelector from '@/components/LanguageSelector';

const supportedLocales = [
  'es',
  'pt',
  'pt-br',
  'de',
  'fr',
  'it',
  'ja',
  'ko',
  'zh',
  'ru',
  'hi',
  'sv',
  'fi',
];

const whatsNewT = {
  en: {
    backHome: '← Back to Home',
    pageTitle: "🆕 What's New",
    latestAdditions: 'Latest Additions',
    subtitle: 'Fresh tabs and tutorials added to DadRock Tabs',
    totalSongs: 'Total Songs',
    communityReviews: 'Community Reviews',
    loading: 'Loading...',
    recentlyAdded: 'Recently added',
    stayUpdated: 'Stay updated with new additions:',
    rss: '📡 Subscribe to RSS Feed',
  },

  es: {
    backHome: '← Volver al inicio',
    pageTitle: '🆕 Novedades',
    latestAdditions: 'Últimas incorporaciones',
    subtitle: 'Nuevas tablaturas y tutoriales añadidos a DadRock Tabs',
    totalSongs: 'Canciones totales',
    communityReviews: 'Reseñas de la comunidad',
    loading: 'Cargando...',
    recentlyAdded: 'Añadido recientemente',
    stayUpdated: 'Mantente al día con las nuevas incorporaciones:',
    rss: '📡 Suscribirse al canal RSS',
  },

  pt: {
  backHome: '← Voltar ao início',
  pageTitle: '🆕 Novidades',
  latestAdditions: 'Adições mais recentes',
  subtitle: 'Novas tablaturas e tutoriais adicionados ao DadRock Tabs',
  totalSongs: 'Total de músicas',
  communityReviews: 'Avaliações da comunidade',
  loading: 'Carregando...',
  recentlyAdded: 'Adicionado recentemente',
  stayUpdated: 'Mantenha-se atualizado com as novas adições:',
  rss: '📡 Assinar o feed RSS',
},

  'pt-br': {
  backHome: '← Voltar ao início',
  pageTitle: '🆕 Novidades',
  latestAdditions: 'Últimas adições',
  subtitle: 'Novas tablaturas e tutoriais adicionados ao DadRock Tabs',
  totalSongs: 'Total de músicas',
  communityReviews: 'Avaliações da comunidade',
  loading: 'Carregando...',
  recentlyAdded: 'Adicionado recentemente',
  stayUpdated: 'Fique por dentro das novas adições:',
  rss: '📡 Assinar o feed RSS',
},

  de: {
  backHome: '← Zur Startseite',
  pageTitle: '🆕 Neuigkeiten',
  latestAdditions: 'Neueste Ergänzungen',
  subtitle: 'Neue Tabs und Tutorials zu DadRock Tabs hinzugefügt',
  totalSongs: 'Lieder insgesamt',
  communityReviews: 'Community-Bewertungen',
  loading: 'Wird geladen...',
  recentlyAdded: 'Kürzlich hinzugefügt',
  stayUpdated: 'Bleibe über neue Ergänzungen auf dem Laufenden:',
  rss: '📡 RSS-Feed abonnieren',
},

  fr: {
  backHome: '← Retour à l’accueil',
  pageTitle: '🆕 Nouveautés',
  latestAdditions: 'Derniers ajouts',
  subtitle: 'Nouveaux onglets et tutoriels ajoutés à DadRock Tabs',
  totalSongs: 'Nombre total de chansons',
  communityReviews: 'Avis de la communauté',
  loading: 'Chargement...',
  recentlyAdded: 'Ajouté récemment',
  stayUpdated: 'Restez informé des nouveaux ajouts :',
  rss: '📡 S’abonner au flux RSS',
},

  it: {
  backHome: '← Torna alla home',
  pageTitle: '🆕 Novità',
  latestAdditions: 'Ultime aggiunte',
  subtitle: 'Nuove tablature e tutorial aggiunti a DadRock Tabs',
  totalSongs: 'Brani totali',
  communityReviews: 'Recensioni della community',
  loading: 'Caricamento...',
  recentlyAdded: 'Aggiunto di recente',
  stayUpdated: 'Resta aggiornato sulle nuove aggiunte:',
  rss: '📡 Iscriviti al feed RSS',
},

  ja: {
  backHome: '← ホームへ戻る',
  pageTitle: '🆕 最新情報',
  latestAdditions: '最新の追加',
  subtitle: 'DadRock Tabs に新しいタブ譜とチュートリアルが追加されました',
  totalSongs: '総曲数',
  communityReviews: 'コミュニティレビュー',
  loading: '読み込み中...',
  recentlyAdded: '最近追加されました',
  stayUpdated: '新しい追加情報をチェックしましょう:',
  rss: '📡 RSSフィードを購読',
},

  ko: {
  backHome: '← 홈으로 돌아가기',
  pageTitle: '🆕 새로운 소식',
  latestAdditions: '최신 추가',
  subtitle: 'DadRock Tabs에 새로운 기타/베이스 탭과 튜토리얼이 추가되었습니다',
  totalSongs: '총 곡 수',
  communityReviews: '커뮤니티 리뷰',
  loading: '불러오는 중...',
  recentlyAdded: '최근 추가됨',
  stayUpdated: '새로운 추가 소식을 확인하세요:',
  rss: '📡 RSS 피드 구독',
},

  zh: {
  backHome: '← 返回首页',
  pageTitle: '🆕 最新动态',
  latestAdditions: '最新添加',
  subtitle: 'DadRock Tabs 新增了新的吉他和贝斯谱及教程',
  totalSongs: '歌曲总数',
  communityReviews: '社区评价',
  loading: '加载中...',
  recentlyAdded: '最近添加',
  stayUpdated: '随时了解最新添加内容：',
  rss: '📡 订阅 RSS 源',
},

  ru: {
  backHome: '← Назад на главную',
  pageTitle: '🆕 Что нового',
  latestAdditions: 'Последние добавления',
  subtitle: 'Новые табулатуры и уроки добавлены в DadRock Tabs',
  totalSongs: 'Всего песен',
  communityReviews: 'Отзывы сообщества',
  loading: 'Загрузка...',
  recentlyAdded: 'Недавно добавлено',
  stayUpdated: 'Следите за новыми добавлениями:',
  rss: '📡 Подписаться на RSS-ленту',
},

  hi: {
  backHome: '← होम पर वापस जाएँ',
  pageTitle: '🆕 नया क्या है',
  latestAdditions: 'नवीनतम जोड़',
  subtitle: 'DadRock Tabs में नए टैब और ट्यूटोरियल जोड़े गए हैं',
  totalSongs: 'कुल गाने',
  communityReviews: 'समुदाय समीक्षाएँ',
  loading: 'लोड हो रहा है...',
  recentlyAdded: 'हाल ही में जोड़ा गया',
  stayUpdated: 'नए जोड़ों की जानकारी प्राप्त करें:',
  rss: '📡 RSS फ़ीड की सदस्यता लें',
},

  sv: {
  backHome: '← Tillbaka till startsidan',
  pageTitle: '🆕 Nyheter',
  latestAdditions: 'Senaste tilläggen',
  subtitle: 'Nya tabs och handledningar har lagts till på DadRock Tabs',
  totalSongs: 'Totalt antal låtar',
  communityReviews: 'Community-recensioner',
  loading: 'Laddar...',
  recentlyAdded: 'Nyligen tillagd',
  stayUpdated: 'Håll dig uppdaterad om nya tillägg:',
  rss: '📡 Prenumerera på RSS-flödet',
},

  fi: {
  backHome: '← Takaisin etusivulle',
  pageTitle: '🆕 Uutta',
  latestAdditions: 'Uusimmat lisäykset',
  subtitle: 'DadRock Tabsiin on lisätty uusia tabulatuureja ja opetusohjelmia',
  totalSongs: 'Kappaleita yhteensä',
  communityReviews: 'Yhteisön arvostelut',
  loading: 'Ladataan...',
  recentlyAdded: 'Lisätty äskettäin',
  stayUpdated: 'Pysy ajan tasalla uusista lisäyksistä:',
  rss: '📡 Tilaa RSS-syöte',
};

export default function WhatsNewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const pathname = usePathname();
  const pathLocale = pathname.split('/')[1];

  const currentLang = supportedLocales.includes(pathLocale)
    ? pathLocale
    : 'en';

  const t = whatsNewT[currentLang] || whatsNewT.en;
  const homeHref = currentLang === 'en' ? '/' : `/${currentLang}`;
    useEffect(() => {
    fetch('/api/whats-new')
      .then((response) => response.json())
      .then((result) => setData(result))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return t.recentlyAdded;

    const localeMap = {
      en: 'en-US',
      es: 'es-ES',
      pt: 'pt-PT',
      'pt-br': 'pt-BR',
      de: 'de-DE',
      fr: 'fr-FR',
      it: 'it-IT',
      ja: 'ja-JP',
      ko: 'ko-KR',
      zh: 'zh-CN',
      ru: 'ru-RU',
      hi: 'hi-IN',
      sv: 'sv-SE',
      fi: 'fi-FI',
    };

    const date = new Date(dateStr);

    return date.toLocaleDateString(
      localeMap[currentLang] || 'en-US',
      {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      }
    );
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
          <header className="border-b border-gray-800 py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
          <Link
            href={homeHref}
            className="text-orange-400 hover:text-orange-300 flex items-center gap-2"
          >
            {t.backHome}
          </Link>

          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-orange-400">
              {t.pageTitle}
            </h1>

            <LanguageSelector
              onLanguageChange={(newLang) => {
                window.location.href =
                  newLang === 'en'
                    ? '/whats-new'
                    : `/${newLang}/whats-new`;
              }}
            />
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-2">
            {t.latestAdditions}
          </h2>

          <p className="text-gray-400">{t.subtitle}</p>

          {data?.stats && (
            <div className="flex justify-center gap-6 mt-4">
              <div className="text-center">
                <span className="text-2xl font-bold text-orange-400">
                  {data.stats.totalSongs}
                </span>
                <span className="text-gray-500 text-sm block">
                  {t.totalSongs}
                </span>
              </div>

              <div className="text-center">
                <span className="text-2xl font-bold text-yellow-400">
                  {data.stats.totalComments}
                </span>
                <span className="text-gray-500 text-sm block">
                  {t.communityReviews}
                </span>
              </div>
            </div>
          )}
        </div>
        {loading ? (
          <div className="text-center text-gray-500">
            {t.loading}
          </div>
        ) : (
          <div className="space-y-3">
            {(data?.recentSongs || []).map((song, i) => (
              <Link
                key={song.slug || i}
                href={
                  currentLang === 'en'
                    ? `/songs/${song.slug}`
                    : `/${currentLang}/songs/${song.slug}`
                }
                className="block bg-gray-900/50 hover:bg-gray-800/50 border border-gray-700/50 hover:border-orange-500/30 rounded-xl p-4 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-orange-400 font-bold text-lg w-8">
                      #{i + 1}
                    </span>

                    <div>
                      <h3 className="font-semibold text-white">
                        {song.title}
                      </h3>

                      <p className="text-sm text-gray-400">
                        {song.artist}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    {song.difficulty && (
                      <span className="text-xs bg-orange-900/50 text-orange-300 px-2 py-1 rounded">
                        {song.difficulty}
                      </span>
                    )}

                    {song.avgRating && (
                      <div className="text-yellow-400 text-xs mt-1">
                        {'★'.repeat(Math.round(song.avgRating))}
                      </div>
                    )}

                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(song.created_at)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
        <div className="mt-10 text-center">
          <p className="text-gray-500 text-sm mb-2">
            {t.stayUpdated}
          </p>

          <a
            href="/api/rss"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-semibold text-sm transition-colors"
          >
            {t.rss}
          </a>
        </div>
      </main>
    </div>
  );
}
