import { createPageLayout } from './layout';
import { createTabPage } from './renderer';

export function buildTabPreview(data = {}) {
  const layout = createPageLayout();
  const page = createTabPage(data);

  return {
    layout,
    page,
    generatedAt: new Date().toISOString(),
  };
}
