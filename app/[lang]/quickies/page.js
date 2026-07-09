import QuickiesClient from '../../quickies/QuickiesClient';

export default function QuickiesPage({ params }) {
  return <QuickiesClient currentLang={params?.lang || 'en'} />;
}
