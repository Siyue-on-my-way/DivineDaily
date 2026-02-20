import { useResponsive } from '../hooks/useResponsive';
import HomePageMobile from './HomePage';
import HomePageDesktop from './HomePageDesktop';

export default function HomePageResponsive() {
  const { isDesktopLayout } = useResponsive();

  return isDesktopLayout ? <HomePageDesktop /> : <HomePageMobile />;
}

