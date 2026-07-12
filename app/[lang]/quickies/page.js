import QuickiesClient from '../../quickies/QuickiesClient';

export default async function QuickiesPage({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'en';

  return <QuickiesClient currentLang={lang} />;
}
