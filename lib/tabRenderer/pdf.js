import { createPageLayout } from './layout';
import { createTabPage } from './renderer';

export function buildTabDocument(data) {
  const layout = createPageLayout();

  const page = createTabPage(data);

  return {
    layout,
    page,
  };
}
