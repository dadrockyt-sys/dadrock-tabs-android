import { PAGE_LAYOUT } from './constants';

export function createPageLayout() {
  return {
    page: {
      width: PAGE_LAYOUT.width,
      height: PAGE_LAYOUT.height,
      marginTop: PAGE_LAYOUT.marginTop,
      marginBottom: PAGE_LAYOUT.marginBottom,
      marginLeft: PAGE_LAYOUT.marginLeft,
      marginRight: PAGE_LAYOUT.marginRight,
    },

    header: {
      x: PAGE_LAYOUT.marginLeft,
      y: PAGE_LAYOUT.marginTop,
      width:
        PAGE_LAYOUT.width -
        PAGE_LAYOUT.marginLeft -
        PAGE_LAYOUT.marginRight,
      height: 70,
    },

    firstStaffY: 140,

    staffSpacing: 120,

    footerY: PAGE_LAYOUT.height - 40,
  };
}
